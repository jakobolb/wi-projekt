from diffusers import AutoPipelineForText2Image, StableDiffusionPipeline
import torch
from utils import flusher
from huggingface_hub import login
import os

# Funktion zur Generierung eines Bildes aus Text-Inputs mit einem Text-zu-Bild-Modell.
# Parameter:
# - prompts: Eine Liste von Text-Prompts, die verwendet werden, um das Bild zu generieren.
# - bool_nprompt: Boolean, um zu steuern, ob ein negatives Prompting (Ausschluss von bestimmten Konzepten) verwendet werden soll.
# - bool_nembedding: Boolean, um zu steuern, ob ein negatives Embedding (wie Textual Inversion) verwendet wird.
# - dif_model: Der Pfad oder Name des Modells, das für die Text-zu-Bild-Generierung verwendet wird.
# Return:
# - image: Das generierte Bild basierend auf den Text-Prompts.
# @auth: David Upatov
def diffusor_worker(prompts, n_prompts, n_embeds, dif_model, enable_fp16=False):
        try:
            login(os.getenv("HUGGINGFACE_API"))
        except:
            print("Login fehlgeschlagen")

        pipe = None

        # Instanziert die Pipe fuer das gewaehlte modell
        if enable_fp16:
            try:
                pipe = AutoPipelineForText2Image.from_pretrained(dif_model, torch_dtype=torch.float16, variant="fp16", use_safetensors=True, safety_checker = None, requires_safety_checker = False)
            except:
                print("Pipe float16 failed roll back to pipe = AutoPipelineForText2Image.from_pretrained(dif_model)")
                pipe = AutoPipelineForText2Image.from_pretrained(dif_model)
        else:
            pipe = AutoPipelineForText2Image.from_pretrained(dif_model)              
        
        # Lade "band_prompt_version2.pt" als textual_inversion bzw. negativ embedding
        try:
            #pipe.load_textual_inversion("./srcs/bad_prompt_version2.pt", token="<wrong>")
            pipe.load_textual_inversion(os.path.join(os.path.dirname(__file__), '..', 'models', 'bad_prompt_version2.pt'), token="<wrong>")
        except:
            print("Load inversion failed") 
        # Check for CUDA (GPU)
        if torch.cuda.is_available():
            pipe = pipe.to("cuda")
        # Check for MPS (Apple Silicon GPU)
        elif torch.backends.mps.is_available():
            pipe = pipe.to("mps")
        # Fallback to CPU
        else:
            print("Using CPU")
            pipe = pipe.to("cpu")
        
        pipe.enable_attention_slicing()

        n_prompt = None

        # Passe je nach Vorauswahl das Negativprompting an
        if (n_embeds):
            n_prompt ="<wrong>"
        if (n_prompts):
            n_prompt ="human, people, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"
        if (n_embeds and n_prompts):
            n_prompt ="<wrong>, human, people, men, women, children, boys, girls, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, extra limbs, disfigured, deformed, body out of frame, bad anatomy, watermark, signature, cut off, low contrast, underexposed, overexposed, bad art, beginner, amateur, distorted face"

             
        
        image = pipe(prompts, negative_prompt = n_prompt).images[0]


        flusher.flushObject(pipe)

        return image

