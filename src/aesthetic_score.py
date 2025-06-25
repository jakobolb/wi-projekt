import torch
from PIL import Image
from transformers import CLIPProcessor
from aesthetics_predictor import AestheticsPredictorV1

#  Berechnet den Ästhetik-Score für ein gegebenes Bild.  
#Parameter:
# - image: Das Bild, das analysiert werden soll. Erwartet ein PIL-Image-Objekt oder ein ähnliches Format, das vom CLIPProcessor verarbeitet werden kann.    
#Return:
# - score_string: Eine Zeichenkette, die den Ästhetik-Score des Bildes enthält, z. B. 'Aesthetic-Score: 4.523'.
# @auth: prog: Jakob Ihler; doc: David Upatov
def get_aestheticscore(image):
    # Load the aesthetics predictor
    model_id = "shunk031/aesthetics-predictor-v1-vit-large-patch14"
    predictor = AestheticsPredictorV1.from_pretrained(model_id)
    processor = CLIPProcessor.from_pretrained(model_id)

    # Preprocess the image
    inputs = processor(images=image, return_tensors="pt")

    # Inference for the image
    with torch.no_grad(): # or `torch.inference_model` in torch 1.9+
        outputs = predictor(**inputs)
    prediction = outputs.logits

    score_string = f"Aesthetic-Score: {round(prediction.item(), 3)}"
    return score_string