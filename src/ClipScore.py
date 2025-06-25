
from transformers import CLIPProcessor, CLIPModel
import torch
import nltk

# Berechnet den CLIP-Score (Ähnlichkeit zwischen Text und Bild)
# Parameter:
# - prompts: Ein String mit der Antwort (Text), die mit dem Bild verglichen werden soll
# - image: Das Bild, das mit dem Text verglichen werden soll (erwartet ein Bildobjekt)
# Return:
# - score_string: Eine Zeichenkette, die den CLIP-Score des Bildes und Textes enthält, z. B. 'CLIP-Score: 0.876'
# @auth: prog: Jakob Olberding; doc: David Upatov
def getClipScore(prompts, image):
    # Lädt das Punkt-Paket von NLTK, das für die Tokenisierung von Texten in Sätze verwendet wird
    nltk.download('punkt')

    # Lädt das vortrainierte CLIP-Modell (Vision Transformer) und den Prozessor
    # zur Text- und Bildverarbeitung, beide stammen von OpenAI's CLIP mit der Vit-Base-Patch32-Architektur
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

    # Zerlegt den Eingabetext `prompts` in Sätze und wählt die ersten beiden Sätze (dieser Teil scheint redundant zu sein)
    sentences = nltk.sent_tokenize(prompts)
    sentences = prompts[:2]

    try:
        # Setzt die `prompts`-Variable als Suchbegriff für das semantische Matching
        semantic_search_phrase = prompts
        # Erstellt Eingaben für das Modell: wandelt Text und Bild in ein geeignetes Format (Tensor) um
        inputs = processor(
            text=[semantic_search_phrase], images=image, return_tensors="pt", padding=True
        )
        # Führt die Vorhersage mit dem CLIP-Modell durch und gibt das Ähnlichkeitsergebnis (logits) für Bild und Text zurück
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image 
        # Wendet Softmax an, um Wahrscheinlichkeiten für Labels zu berechnen (optional für Labelwahrscheinlichkeiten)
        probs = logits_per_image.softmax(dim=1) 

        logits_per_image = outputs.logits_per_image
        # Extrahiert den Ähnlichkeitswert und konvertiert ihn in eine Liste
        score = logits_per_image.squeeze().tolist()
        # Formatiert den Wert als CLIP-Score mit drei Dezimalstellen
        score_string = f"CLIP-Score: {round(score, 3)}"

        # Gibt den Score-String zurück
        return score_string
        
        
    except:
        # Ausnahmebehandlung, falls ein Fehler auftritt, führt den gleichen Prozess erneut aus
        # Tokenisiert den Text in Sätze und verwendet nur die ersten beiden Sätze
        prompts = nltk.sent_tokenize(prompts)
        prompts = prompts[:2]

        # Wiederholung des Prozesses zum Erstellen der Eingaben und zur Berechnung des CLIP-Scores
        semantic_search_phrase = prompts

        inputs = processor(
            text=[semantic_search_phrase], images=image, return_tensors="pt", padding=True
        )
        outputs = model(**inputs)
        logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
        probs = logits_per_image.softmax(dim=1)  # we can take the softmax to get the label probabilities

        logits_per_image = outputs.logits_per_image
        score = logits_per_image.squeeze().tolist()
        
        # Formatiert und gibt den CLIP-Score zurück
        score_string = f"CLIP-Score: {round(score, 3)}"

        return score_string
        