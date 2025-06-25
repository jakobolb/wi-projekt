from openai import OpenAI
import requests
from PIL import Image
import io
import os

# Erstellt einen OpenAI-Client und lädt den API-Schlüssel aus den Umgebungsvariablen
client = OpenAI(
    api_key = os.environ.get("OPENAI_API_KEY"),
)

# Ruft die OpenAI GPT-API auf, um einen Textvorschlag zu generieren
# Parameter:
# - gpt_model: Das GPT-Modell, das verwendet werden soll (z.B. "gpt-3.5-turbo")
# - systemprompt: Der System-Prompt, um den Kontext oder Anweisungen für das Modell festzulegen
# - product: Das Produkt, für das der Textvorschlag generiert werden soll
# - DataString: Weitere benutzerdefinierte Informationen für den Vorschlag
# Return:
# - Gibt den generierten Text aus der API zurück (1. Vorschlag aus der Liste)
# @auth: David Upatov
def callGPTAPI(llm_option, llm_sys_prompt, product, topics):

    completion = client.chat.completions.create(
    model=llm_option,
    max_tokens=75,
    #temperatur zeigt wie randome der output ist <1 wenig randome >1 mehr random =1 ausgeglichen
    temperature=1,
    messages=[
        {"role": "system", "content": f"{llm_sys_prompt}"},
        {"role": "user", "content": f"describe an image to advertise a {product} for someone interested in the following: {topics}"}
    ]
    )

    
    return completion.choices[0].message.content

# Ruft die DALL·E API auf, um ein Bild basierend auf einem Prompt zu generieren
# Parameter:
# - dall_e_modell: Das Modell von DALL·E, das verwendet werden soll bsp "dall-e-3"
# - prompt: Der Text, auf dessen Basis das Bild generiert werden soll
# Return:
# - Gibt das generierte Bild als PIL-Image-Objekt zurück
# @auth: David Upatov
def callDALLE(dif_model, prompts):

    response = client.images.generate(
                model=dif_model,
                prompt=prompts,
                size="512x512",
                quality="standard",
                n=1,
                )

    image_url = response.data[0].url

    response = requests.get(image_url)
    in_memory_file = io.BytesIO(response.content)
    im = Image.open(in_memory_file)
    return im
