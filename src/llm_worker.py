import torch 
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline 
import os
from huggingface_hub import login
#from mlx_lm import load, generate
from utils import flusher

# Gibt ein standardisiertes System-Prompt zurück, das für die Bildgenerierung verwendet wird.
# Return:
# - sys_prompt: Ein String, der das System-Prompt enthält, das der KI beschreibt, wie Werbebilder generiert werden sollen.
# @auth: David Upatov
def standard_sys_prompt():
    sys_prompt ="""You are an art director who uses an image-generating \ AI to create advertisment images for a specific product. In order for the AI to generate good images,\
          you use the following pattern: An image, with no people, of [product] [adjective] [subject] [doing action], [creative lighting style], detailed, realistic, trending on artstation, in style of [advertisment image style]"""
    return sys_prompt

# Arbeiterfunktion, die ein Large Language Model (LLM) für die Bildbeschreibung und -generierung verwendet.
# Parameter:
# - llm_option: Der Pfad oder Name des Modells, das verwendet werden soll.
# - lm_sys_prompt: Der System-Prompt, der das Verhalten des Modells festlegt.
# - product: Das zu bewerbende Produkt.
# - topics: Eine zusätzliche Beschreibung oder Daten, die im Prompt verwendet werden sollen.
# Return:
# - output[0]['generated_text']: Der generierte Text des Modells, der die Bildbeschreibung enthält.
# @auth: David Upatov
def llm_worker(llm_option:str, llm_sys_prompt:str, product:str, topics:str):

    device = ""

    try:
        login(os.getenv("HUGGINGFACE_API"))
    except:
        print("Login fehlgeschlagen")


    # Check for CUDA (GPU)
    if torch.cuda.is_available():
        device= "cuda"
        
    elif torch.backends.mps.is_available():
        device= "mps"
    # Fallback to CPU
    else:
        device= "cpu"

    print("Device: ", device)


    torch.random.manual_seed(0) 
    model = AutoModelForCausalLM.from_pretrained( 
        llm_option,  
        device_map=device,  
        torch_dtype=torch.bfloat16,  
        trust_remote_code=True,  
    ) 

    tokenizer = AutoTokenizer.from_pretrained(llm_option) 

    messages = [ 
        {"role": "system", "content": llm_sys_prompt}, 
        {"role": "user", "content":  f"describe an image to advertise a {product} for someone interested in the following: {topics}"}, 
    ] 

    pipe = pipeline( 
        "text-generation", 
        model=model, 
        tokenizer=tokenizer, 
    ) 

    generation_args = { 
        "max_new_tokens": 70, 
        "return_full_text": False, 
        "temperature": 0.0, 
        "do_sample": False, 
    } 

    output = pipe(messages, **generation_args) 
    print("Antwort:")
    print(output[0]['generated_text']) 
    print("Ende")

    flusher.flushObject(pipe)
    return output[0]['generated_text']
