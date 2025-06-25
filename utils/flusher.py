
import gc
import torch


# Fuehrt gc aus und entlehrt den mps cache
# @auth: David Upatov
def flush():
    gc.collect()

    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    
# Loescht das uebergebene Object und fuehrt flush aus 
# @auth: David Upatov
def flushObject(Object):
    try:
        Object
    except NameError:
        print("Object is not exiting")
    else:
        del Object

    flush()