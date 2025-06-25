from transformers import AutoTokenizer, AutoModelForCausalLM
from utils import flusher

# Instanziert ein LLM zur evaluation von StableDiffusion Prompts ueber HuggingfaceHUb
# Wird leider nicht empfohlen, da oft wichtige Prompts geloescht werden.
# @llm_text: Prompts welche evaluiert werden sollen.
# @auth: David Upatov

def infarenceBloom(prompts):

    device = "mps"

    tokenizer = AutoTokenizer.from_pretrained('alibaba-pai/pai-bloom-1b1-text2prompt-sd-v2')
    model = AutoModelForCausalLM.from_pretrained('alibaba-pai/pai-bloom-1b1-text2prompt-sd-v2').to(device)
    raw_prompt = prompts

    TEMPLATE_V2 = 'Converts a simple image description into a prompt. \
    Prompts are formatted as multiple related tags separated by commas, plus you can use () to increase the weight, [] to decrease the weight, \
    or use a number to specify the weight. You should add appropriate words to make the images described in the prompt more aesthetically pleasing, \
    but make sure there is a correlation between the input and output.\n\
    ### Input: {raw_prompt}\n### Output:'

    input = TEMPLATE_V2.format(raw_prompt=raw_prompt)
    input_ids = tokenizer.encode(input, return_tensors='pt').to(device)
    #input_ids = tokenizer.encode(input, return_tensors='pt').cuda()
    outputs = model.generate(
        input_ids,
        max_new_tokens=77,
        do_sample=True,
        temperature=0.9,
        top_k=50,
        top_p=0.95,
        repetition_penalty=1.1)

    prompts = tokenizer.batch_decode(outputs[:, input_ids.size(1):], skip_special_tokens=True)
    prompts = [p.strip() for p in prompts]

    flusher.flushObject(tokenizer)
    flusher.flushObject(model)

    
    prompt_string = " ".join(prompts)
     

    return prompt_string