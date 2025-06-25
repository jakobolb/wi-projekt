import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv(override=True)

from src import ChatGPTPipe as gpt
from utils import htmlreader
from src import Promptevaluation
from src import ClipScore as clip
from src import aesthetic_score as a_score
from src import output_manager as om
from src import llm_worker as lw
from src import diffusor_worker as dw
from utils import json_manager as jm

from Database import database as db

from src import bg_inpaint as ipnt


from PIL import Image
import re

# Sucht im String nach int-Wert und gibt diesen zurueck.
# @string: String aus dem nach einem der Int-Wert extrahiert werden soll
def extract_number(string):
    #Regex um Zahlen zu extrahieren
    pattern = r'\d+'
    
    #match fuer regex
    match = re.search(pattern, string)
    
    #wenn match, dann gib nummer als int zurueck
    if match:
        return int(match.group())
    else:
        return None


# Setzt die Elemente in der UI auf "weit"
st.set_page_config(layout="wide")

# Workflow Variablen:
if 'clip_score_trashhold' not in st.session_state:
    st.session_state['clip_score_trashhold'] = 30
repeat_limit = None




# OpenAI Modelleinstellungen
gpt_whitelist = ["gpt-4", "gpt-4o", "gpt-3.5-turbo", "dall-e-2", "dall-e-3"]



#Sessionsattes
if 'alias' not in st.session_state:
    st.session_state['alias'] = ""

if 'ad_object' not in st.session_state:
    st.session_state['ad_object'] = ""


# Diese Funktion generiert Bilder basierend auf dem angegebenen Diffusionsmodell und den Prompts.
# Sie zeigt den Fortschritt in der Benutzeroberfläche an, bewertet die generierten Bilder anhand von 
# CLIP-Score und speichert die Ergebnisse sowohl im Dateisystem als auch in einer Datenbank.

# Parameter:
# - dif_model: Das verwendete Diffusionsmodell (z.B. Dall-E-3 oder Stable Diffusion).
# - prompts: Die Textprompts, die zur Bildgenerierung verwendet werden.
# - error_img: Ein Bild, das angezeigt wird, wenn ein Fehler bei der Generierung auftritt.
# - clip_score: Boolean, der angibt, ob der CLIP-Score zur Bewertung der Bilder verwendet werden soll.
# - clip_score_trashhold: Der Schwellenwert, den der CLIP-Score erreichen muss, um das Bild als akzeptabel zu betrachten.
# - alias: Ein Alias für die Person, die mit den generierten Bildern assoziiert wird.
# - ad_object: Das Objekt, das in den generierten Bildern hervorgehoben werden soll.
# - limit_rep: Boolean, der angibt, ob die Anzahl der Bildgenerierungen begrenzt werden soll.
# - rep_limit: Die maximale Anzahl der erlaubten Wiederholungen bei der Bildgenerierung, wenn limit_rep aktiv ist.
# - col: Eine Nummer, die angibt, in welcher Spalte das generierte Bild angezeigt werden soll.
#@auth: David Upatov
def workflow_column(dif_model, prompts, error_img, clip_score, clip_score_trashhold, alias, product, limit_rep, rep_limit, enable_fp16,  col):
    st.header(dif_model)

    # Initialisiere Nummer Runde
    round_generating = 1

    # Wenn diffusermodell in der OpenAI Whitelist ist, wird Dall-E endpunkt abgerufen
    if dif_model in gpt_whitelist:
        with st.spinner('Generiert Bild...'):
            try:
                image = gpt.callDALLE(dif_model, prompts)
            except:
                image = error_img
            
            dif_clip = clip.getClipScore(prompts, image)

    # Wenn diffusormodell nicht in der OpenAI Whitleist ist, wird Huggingface Modell geladen
    else:
        # Generiere mit Stable Diffusion 1.4 so oft Bilder, bis eines einen Clip-Score >= 30 hat
        rounds = 0
        dif_clip = "Clip Score: 1"

        # Clip gibt den Score als str zurueck, deswegen muss extra die Nummer aus dem String extrahiert werden und geprueft werden ob es es kleiner als der Trahold ist
        while extract_number(dif_clip) < clip_score_trashhold:
            with st.spinner('Generiert Bild Runde: '+ str(round_generating)):

                try:        
                    # Generiere Bild mit Diffusormodell aus Github          
                    image = dw.diffusor_worker(prompts, n_embeds, n_prompts, dif_model, enable_fp16=enable_fp16)
                    if clip_score:
                        try:
                            # Generiere Clipscore
                            dif_clip = clip.getClipScore(prompts, image)
                        except Exception as e: 
                            print("Error: ",e)
                            # Dieser Wert soll helfen festzustellen wo genau der Fehler hergekommen ist
                            dif_clip = "4042"
                    else:
                        # Dieser Wert soll helfen festzustellen wo genau der Fehler hergekommen ist
                        dif_clip = "4041"
                except Exception as e: 
                    # Dieser Wert soll helfen festzustellen wo genau der Fehler hergekommen ist
                    print("Error: ",e)
                    v = error_img
                    dif_clip = "Clip Score: 404"
                
                # Wenn Limiter gesetzt wurde und Runde der Generierung den limit erreicht hat, bricht die While-Schleife
                if limit_rep == True and round_generating >= rep_limit:
                    break

                
                rounds += 1
                round_generating += 1

    # Zeigt Bild und alle Scores die im Workflow definiert wurden
    st.image(image)
    if clip_score:
        st.write("Clipscore: " + dif_clip)
    if asthetic_score:
        st.write("Aesthetic Score: " + str(a_score.get_aestheticscore(image)))

    # Speicher das Bild im output-Ordner
    om.safe_image(image, st.session_state['alias'], st.session_state['alias'] + "_dif" + str(col) + ".png")
    st.markdown(":green[Bilder wurden im Ordner output/"+ st.session_state['alias'] +" gesichert!]")

    # Speicher das Bild in Vektordatenbank
    try:
        db.insert_image(alias, product, topics, prompts, dif_model, llm_option, image)
        st.markdown(":green[Bilder wurden in der Datenbank gesichert]")
    except:
        #db.initiate_table
        st.markdown(":red[Bild konnte nicht in der Datenbank gesichert werden]")



# Errorbild fuer exceptionhandling
error_img = Image.open(os.path.join(os.path.dirname(__file__), "error_picture.jpg"))

st.title("WI-Projekt generative advertisement")

# Auswahlmenü für verschiedene Seiten in der Anwendung
page = st.sidebar.selectbox("Wähle eine Seite",["Advertisement Image Generator", "Advertisment Image Masking"])



################---------Advertisment Image Masking------------############
if page == "Advertisment Image Masking":
    st.header("Advertisment Image Masking")

    sel_col1, sel_col2, sel_col3, sel_col4 = st.columns(4)


    # Dropdown LLM
    llms = [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.dirname(__file__), "src", "LLMs")) if f.endswith('.json')]
 

    # Lade alle LLMs die gespeicht wurden in einem Dropdown Menu zum auswaehlen
    with sel_col1:
        llm_option = st.selectbox(
            "Select LLM",
            llms
        )

    # Liest den Huggingface Pfad aus gewahelten LLM 
    llm_daten = jm.llm_auslesen(llm_option)
    llm_option = llm_daten["LLM_path"]

    # File Uploader fuer HTML Werbedaten
    with sel_col2:
        uploaded_file = st.file_uploader("Upload HTML", type=["html", "HTML"] )
        if uploaded_file:
            try:
                topics = htmlreader.list_to_string(htmlreader.pick_random(htmlreader.ListInterest(uploaded_file),3))
            except Exception as e:
                st.write("Error: ", e)
                st.write("Bitte lade eine your_topics.html von den Meta-Werbedaten hoch.")
    with sel_col3:
        # Funktion, um den Mittelpunkt eines Bildes zu berechnen
        def calculate_center(image):
            width, height = image.size
            center_x = width / 2
            center_y = height / 2
            return center_x, center_y

        # File Uploader lässt nur Bildaten in png und jpg Format zu.
        ad_object_image = st.file_uploader("Upload Ad-Object, the object must be in the centre", type=["jpg", "png", "JPG", "PNG"])

        # Wenn ein Bild hochgeladen wurde, wird die Postion des mittleren Pixels gesucht und wierdergegeben.
        if ad_object_image is not None:

            image = Image.open(ad_object_image)
            center_x, center_y = calculate_center(image)

            st.write("center_x: " + str(center_x) + "; center_y:" + str(center_y))

    # Hochgeladenes Bild wird dargestellt
    with sel_col4:
        if ad_object_image:
            st.image(ad_object_image)
        
    # Startet generierung des Bildes    
    if st.button("Start"):

        if llm_option and ad_object_image and uploaded_file:
            # Umgeschriebener Systemprompt fuer das LLM, da hier kein String mit dem Produkt weitergegeben wird und auch nicht muss, da kein Bild vom Produkt generiert werden muss
            llm_sys_prompt = """You are an art director who uses an image-generating \ AI to create advertisment backgroundimages. In order for the AI to generate good images,\
          you use the following pattern: An image, with no people, of [object] [doing action], [creative lighting style], detailed, realistic, trending on artstation, in style of [advertisment image style]"""

            # Wenn LLM-Modell in got_whitelist ist wird OpenAI Endpunkt aufgerufen
            if llm_option in gpt_whitelist:
                prompts = gpt.callGPTAPI(llm_option, llm_sys_prompt ,"", topics)
                st.write("GPT Prompts: " + prompts)

            # Wenn LLM-Modell nicht in got_whitelist Model aus Huggingface benutzt
            else:
                with st.spinner('Loading or Downloading LLM'):
                    prompts = lw.llm_worker(llm_option, llm_sys_prompt, "", topics)
                    st.write("Prompts: " + prompts)


            image_col1, image_col2, image_col3 = st.columns(3)

            # Generiere 3 Bilder mit inpaint.
            with image_col1:
                with st.spinner('Generate Image'):
                    try:
                        inpaint_image1 = ipnt.bg_inpaint(ad_object_image, prompts, center_x, center_y)
                        st.image(inpaint_image1)
                    except Exception as e:
                        st.image(error_img)
                        st.write("Error: ", e)

            with image_col2:
                with st.spinner('Generate Image'):
                    try:
                        inpaint_image2 = ipnt.bg_inpaint(ad_object_image, prompts, center_x, center_y)
                        st.image(inpaint_image2)
                    except Exception as e:
                        st.image(error_img)
                        st.write("Error: ", e)

            with image_col3:
                with st.spinner('Generate Image'):
                    try:
                        inpaint_image3 = ipnt.bg_inpaint(ad_object_image, prompts, center_x, center_y)
                        st.image(inpaint_image3)
                    except Exception as e:
                        st.image(error_img)
                        st.write("Error: ", e)

#############################################################################
                

###############---------Advertisement Image Generator------------############
if page == "Advertisement Image Generator":

    st.header("Advertisement Image Generator")

    # Bereich um selber einen Worklfow zu kalibrieren bzw zu erstellen.
    with st.expander("Create Workflow"):
        
        st.info("Enabling float16 can cause a NSFW/Blackpicture-Bug for some models.")

        # Hier kann ein Name fuer den Worklfow definiert werden
        wf_name = st.text_input("Workflow Bezeichnung:")
        # Nur Bachstaben Zahlen und Leerzeichen erlauben
        if wf_name:
            filtered_name = re.sub(r'[^a-zA-Z0-9_-]', '', wf_name) 
            if wf_name != filtered_name:
                st.warning("Nur Buchstaben, Zahlen, Bindestriche (-) und Unterstriche (_) sind erlaubt.")
            wf_name = filtered_name

        wf_col1, wf_col2, wf_col3, wf_col4 = st.columns(4)

        # Hier kann fuer jeden der 3 Diffusor Modelle ein Huggingface Pfade definiert werden oder der Name eines Modells aus der gpt_whitelist
        with wf_col1:
            wf_dif1_model = st.text_input("Path of first diffusor model (dif1)")
            enable_dif1_fp16 = st.checkbox("Enable float16 (dif1)", key="fb16dif1")
        with wf_col2:
            wf_dif2_model = st.text_input("Path of second diffusor model (dif2)")
            enable_dif2_fp16 = st.checkbox("Enable float16 (dif2)", key="fb16dif2")
        with wf_col3:
            wf_dif3_model = st.text_input("Path of third diffusor model(dif3)")
            enable_dif3_fp16 = st.checkbox("Enable float16 (dif3)", key="fb16dif3")
        with wf_col4:
            llm_sys_prompt = st.text_input("LLM-system-prompt", value=lw.standard_sys_prompt())

        cust_col1, cust_col2, cust_col3, cust_col4, cust_col5, cust_col6, cust_col7= st.columns(7)
        # Wennn Dropdown-> Customize dann erscheinen Checkboxen um eine Auswahl zu machen, welche Parameter dazugeschalten werden
        # n_prompts: Parameter um negative Prompts im Diffusor.Modell zu nutzen
        with cust_col1:
            n_prompts = st.checkbox("Standard negativ prompts")
        # n_embeds: Parameter um negative Embeddings im Diffusor.Modell zu nutzen
        with cust_col2:
            n_embeds = st.checkbox("Negativ embeddings")
        # prompt_evaluation: Parameter um ein LLM Modell zu nutzen um das generierte Prompt zu verbessern
        with cust_col3:
            prompt_evaluation = st.checkbox("Promptevaluation")
        # clip_score: Parameter um einen Clipü-Score zu berechnen, welcher zeigt wie nahe das Bild mit dem Prompt uebereinstimmt  
        with cust_col4:
            clip_score =st.checkbox("Clip-Score")
        # clip_score_trashold: hoehe des Clip-Score die ueberschritten werden muss, anderfalls wird eine erneute Generierung angestossen.
        with cust_col5:
            st.session_state['clip_score_trashhold'] = st.number_input("Clip-Score Trashhold", value=30, min_value=20, max_value=40)
        # astetic_score: Parameter um einen Astehtic-Score zu berechnen, welcher zeigt wie esthetisch die Bildelemente im Bild sind.
        with cust_col6:
            asthetic_score = st.checkbox("Asthetic-Score")
        # repeat_limit: Limiter fuer Bildgenerierungsinterationen.
        with cust_col7:
            limit_repetitions = st.checkbox("Limit Image-Gen repetitions")
            if limit_repetitions:
                repeat_limit = st.number_input("Limit number of Image-Gen repetitions", value=2, min_value=1, max_value=99)


        # Dict Objekt welches alle Parameter zusammenfasst
        wf_daten = {
            "n_prompts": n_prompts,
            "n_embeds": n_embeds,
            "prompt_evaluation": prompt_evaluation,
            "clip_score": clip_score,
            "clip_score_trashhold": st.session_state['clip_score_trashhold'],
            "asthetic_score": asthetic_score,
            "wf_dif1_model": wf_dif1_model,
            "wf_dif2_model": wf_dif2_model,
            "wf_dif3_model": wf_dif3_model,
            "llm_sys_prompt": llm_sys_prompt,
            "limit_repetitions": limit_repetitions,
            "repeat_limit": repeat_limit,
            "enable_dif1_fp16": enable_dif1_fp16,
            "enable_dif2_fp16": enable_dif2_fp16,
            "enable_dif3_fp16": enable_dif3_fp16
        }

        # Speichert Dict Objekt als Json und macht es modular und persistent
        if st.button("Workflow Speichern"):
            jm.wf_speichern(wf_daten, wf_name)
            st.markdown(":green[Workflow erfogreich gespeichert]")

    # Bereich um LLM-Pfade persistent zu sichern.
    with st.expander("Add LLM"):

        # Eingabe eines Huggingface Pfads fuer ein LLM-Modell
        llm_path = st.text_input("Huggingface Path of LLM")
        # Trennt den Namen des Modells vom Namen des Herstellers
        llm_name = llm_path.split('/')[-1]
        # Dict Objekt um alle Informationen zusammenzufassen
        llm_daten = {
            "LLM_path": llm_path,
            "LLM_name": llm_name
        }
        if st.button("LLM Speichern"):
            # Speichern des Dict Objekts um es Modular und Persitent zu machen
            jm.llm_speichern(llm_daten, llm_name)
            st.markdown(":green[LLM erfogreich gespeichert]")

    # Container fuer 2 Dropdownmenues
    sel_col1, sel_col2, sel_col3 = st.columns(3)

    # Lade alle LLM-Namen aus dem LLM Ordner
    llms = [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.dirname(__file__), "src", "LLMs")) if f.endswith('.json')]

    # Liste alle LLMs auswaehlbar in einem Dropdown
    with sel_col1:
        llm_option = st.selectbox(
            "Select LLM",
            llms
        )

    # Lese den Huggingfacepfad des gewaehlten LLMs // oder Modellnamen falls es ein OpenAI-Modell ist
    llm_daten = jm.llm_auslesen(llm_option)
    llm_option = llm_daten["LLM_path"]

    # Lade alle Workflow-Namen aus dem Workflow Ordner
    Workflows = [os.path.splitext(f)[0] for f in os.listdir(os.path.join(os.path.dirname(__file__), "src","Workflows")) if f.endswith('.json')]    

    # Liste alle Workflows auswaehlbar in einem Dropdown
    with sel_col2:
        flow_option = st.selectbox(
            "Select Workflow",
            Workflows)

    #Laden aller Workflow-Variablen
    wf_daten = jm.wf_auslesen(flow_option)

    #Zuweisen aller Workflow-Variablen
    n_prompts = wf_daten["n_prompts"]
    n_embeds = wf_daten["n_embeds"]
    prompt_evaluation = wf_daten["prompt_evaluation"]
    clip_score = wf_daten["clip_score"]
    clip_score_trashhold = wf_daten["clip_score_trashhold"]
    asthetic_score = wf_daten["asthetic_score"]
    wf_dif1_model = wf_daten["wf_dif1_model"]
    wf_dif2_model = wf_daten["wf_dif2_model"]
    wf_dif3_model = wf_daten["wf_dif3_model"]
    llm_sys_prompt = wf_daten["llm_sys_prompt"]
    limit_repetitions = wf_daten["limit_repetitions"]
    repeat_limit = wf_daten["repeat_limit"]
    enable_dif1_fp16 = wf_daten["enable_dif1_fp16"]
    enable_dif2_fp16 = wf_daten["enable_dif2_fp16"]
    enable_dif3_fp16 = wf_daten["enable_dif3_fp16"]

    #Delete Button um Workflow zu löschen.
    with sel_col3:
        if st.button("delete workflow"):
            if os.path.exists("src/Workflows/"+ flow_option + ".json"):
                os.remove("src/Workflows/"+ flow_option + ".json")
                st.success(f"Workflow {flow_option} gelöscht")

    #Expander um kompletten Workflow zu überprüfen.
    with st.expander("Details"):
        st.text(f"llm={llm_option};dif1={wf_dif1_model};dif2={wf_dif2_model};dif3={wf_dif3_model};n_prompts={n_prompts}")
        st.text(f"enable_dif1_fp16={enable_dif1_fp16};enable_dif2_fp16={enable_dif2_fp16};enable_dif3_fp16={enable_dif3_fp16};")
        st.text(f"n_embeds={n_embeds};prompt_evaluation{prompt_evaluation};clip_score={clip_score};clip_trashhold={clip_score_trashhold}")
        st.text(f"astehtic_score={asthetic_score};llm_sys_promt={llm_sys_prompt}")

    # Container um im Freitext einen Alias fuer den Probanden anzugeben, und ein String fuer den zu umwerbenden Gegenstand
    in_col1, in_col2 = st.columns(2)

    with in_col1:
        st.session_state['alias'] = st.text_input("Person Alias:", st.session_state['alias'])
    with in_col2:
        st.session_state['ad_object'] = st.text_input("Advertisment Object:", st.session_state['ad_object'])


    # Wenn alle Felder ausgefuellt wurden erscheint ein Dropdownmenu um auszuwaehlen ob man eine HTML Datei hochladen moechte mit den Werbeinteressen oder ob man einen String mit interessen eingaben will.
    if st.session_state['ad_object'] and st.session_state['alias']:
        select_topic_upload = st.selectbox(
            "Select Topics input variant",
            ["Textfield","Upload your_topics.html"]
        )

        #Muss deklariert werden, weil sonst funktioniert if-Abfrage nicht
        uploaded_file = None
        selected_topics_text = None

        #Upload einer Werbedaten HTML Datei von Meta
        if select_topic_upload == "Upload your_topics.html":
            uploaded_file = st.file_uploader("Choose a file", type=["html", "HTML"])

        #Eingabe von Werbetopics per Text
        if select_topic_upload == "Textfield":
            selected_topics_text = st.text_input("Topic:")

        if uploaded_file is not None or selected_topics_text is not None:
            
            # Wenn Upload you_topics.html, dann zeig das Upload funktioniert hat
            if select_topic_upload == "Upload your_topics.html":
                st.markdown(":green[HTML-File upload complete.]")
            # WEnn Textfeld Eingabe, dann zeigt das Text akzeptiert wurde
            if select_topic_upload == "Textfield":
                st.markdown(":green[Topics selected by text.]")

            # Wenn alle Vorkehrungen getroffen wurden erscheint ein Button, mit dem man die Vorauswahl bestaetigen kann um die Bilder zu generieren
            if st.button("Generate Advertisements"):

                #topics= None
                if select_topic_upload == "Upload your_topics.html":
                    topics = htmlreader.list_to_string(htmlreader.pick_random(htmlreader.ListInterest(uploaded_file),3))
                if select_topic_upload == "Textfield":
                    topics = selected_topics_text

                
                # Wenn beim LLM-Dropdown GPT gewaehlt wurde, dann wird die openAI API abgerufen, um basierend auf die topics und dem Objekte Prompts zu generieren.
                if llm_option in gpt_whitelist:

                    prompts = gpt.callGPTAPI(llm_option ,llm_sys_prompt ,st.session_state['ad_object'], topics)
                    st.write("GPT Prompts: " + prompts)

                else:
                    with st.spinner('Loading or Downloading LLM'):
                        prompts = lw.llm_worker(llm_option, llm_sys_prompt, st.session_state['ad_object'], topics)
                        st.write("Prompts: " + prompts)

                # Sollte die Option "Promptevaluation" gewaehlt worden sein, wird das LLM "Bloom" zwischengeschaltet um die LLM-Prompts auf Image-Gen Standards anzupassen (Funktioniert aber nicht so gut)
                if prompt_evaluation:
                    with st.spinner('Evaluate prompt'):
                        prompts = Promptevaluation.infarenceBloom(prompts)
                        st.write("Evaluated Prompts: " + prompts)

                # Container um Bilder zu generieren und generierte Bilder anzuzeigen
                col1, col2, col3 = st.columns(3)

                # Generiere ein Bild fuer jeder Gewahelt Objekt und zeig sie nebeneinander auf.
                with col1:
                    
                    workflow_column(wf_dif1_model, prompts, error_img, clip_score, clip_score_trashhold, st.session_state['alias'], st.session_state['ad_object'], limit_repetitions, repeat_limit, enable_dif1_fp16, 1)

                with col2:
                    workflow_column(wf_dif2_model, prompts, error_img, clip_score, clip_score_trashhold, st.session_state['alias'], st.session_state['ad_object'], limit_repetitions, repeat_limit, enable_dif2_fp16, 2)
                
                with col3:
                    workflow_column(wf_dif3_model, prompts, error_img, clip_score, clip_score_trashhold, st.session_state['alias'], st.session_state['ad_object'], limit_repetitions, repeat_limit, enable_dif3_fp16, 3)

                
                

                

                



            

                



