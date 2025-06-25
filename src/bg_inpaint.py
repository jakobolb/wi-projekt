import cv2
import math
import numpy as np
#from convert import bgremove5, applyMask
import scipy.ndimage as morph
from diffusers import AutoPipelineForInpainting
from diffusers.utils import load_image, make_image_grid
import torch
from PIL import Image
import matplotlib.pyplot as plt
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor

# Führt Inpainting (Hintergrundrekonstruktion) auf einem Bild durch und verwendet ein prompt, um den Hintergrund zu generieren.
# Parameter:
# - image: Das Bild, auf das das Inpainting angewendet wird.
# - prompt: Der Textprompt, der verwendet wird, um den Hintergrund zu erzeugen.
#@auth: prog: Jokob Olberding doc: David Upatov
def bg_inpaint (ad_object_image, prompts, center_x, center_y):

    # install Text-to-Image modell
    pipe = AutoPipelineForInpainting.from_pretrained(
    "kandinsky-community/kandinsky-2-2-decoder-inpaint",
    torch_dtype=torch.float32
    )
    if torch.cuda.is_available():
       pipe.to("cuda")
    elif torch.backends.mps.is_available():
       pipe.to("mps")
    else:
       pipe.to("cpu")

    # Use sam2 for Object Recognition
    device = torch.device("cpu")
    sam2_checkpoint = "wi_projekt_generative_ad/models/sam2_hiera_large.pt" #evtl Pfad anpassen
    model_cfg = "sam2_hiera_l.yaml"
    sam2_model = build_sam2(model_cfg, sam2_checkpoint, device=device)
    predictor = SAM2ImagePredictor(sam2_model)

    # read Image
    img = Image.open(ad_object_image)
    # specify point on foreground/object for segmentation
    input_point = np.array([[center_x, center_y]])
    input_label = np.array([1])
    #plt.figure(figsize=(10, 10))
    #plt.imshow(img)
    #show_points(input_point, input_label, plt.gca())
    #plt.axis('on')


    # set image
    predictor.set_image(img)
    # segment image by providing point and label
    # multimask_output=True returns multiple segmentation masks with varying confidence thresholds
    masks, scores, logits = predictor.predict(
        point_coords=input_point,
        point_labels=input_label,
        multimask_output=True,
    )
    # sort masks according to confidence scores
    sorted_ind = np.argsort(scores)[::-1]
    masks = masks[sorted_ind]
    scores = scores[sorted_ind]
    logits = logits[sorted_ind]
    # plot most confident mask
    #plt.imshow(img)
    #show_mask(masks[0], plt.gca(), random_color=True)
    #plt.axis('off')
    #plt.figure(figsize=(10, 10))
    binary_img = np.invert(masks[0].astype(bool)).astype(np.uint8)
    binary_img = Image.fromarray(binary_img*255).resize((512, 512))
    img = img.resize((512, 512))

    # create new image
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    generator = torch.Generator(device).manual_seed(92)
    # generate backgrounds
    negative_prompt = "artifacts, low quality, distortion"
    created_img = pipe(
        prompt=prompts, image=img, mask_image=binary_img, generator=generator).images[0]
    return created_img

# Zeigt die Segmentierungsmaske an, die auf das Bild angewendet wird.
# Parameter:
# - mask: Die Maske, die auf das Bild angewendet wird.
# - ax: Die Achse des Plots, auf der die Maske angezeigt wird.
# - random_color: Wenn True, wird eine zufällige Farbe für die Maske verwendet.
# - borders: Zeigt die Konturen der Maske an, wenn True.
#@auth: prog: Jokob Olberding doc: David Upatov
def show_mask(mask, ax, random_color=False, borders=True):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask = mask.astype(np.uint8)
    mask_image = mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    if borders:
        import cv2
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        # Try to smooth contours
        contours = [cv2.approxPolyDP(
            contour, epsilon=0.01, closed=True) for contour in contours]
        mask_image = cv2.drawContours(
            mask_image, contours, -1, (1, 1, 1, 0.5), thickness=2)
    ax.imshow(mask_image)

# Zeigt Punkte (z.B. zur Segmentierung) auf dem Bild an.
# Parameter:
# - coords: Die Koordinaten der Punkte, die angezeigt werden sollen.
# - labels: Labels für die Punkte, z.B. 1 für positive Punkte.
# - ax: Die Achse des Plots, auf der die Punkte angezeigt werden.
# - marker_size: Die Größe der Marker, die die Punkte darstellen.
    #@auth: prog: Jokob Olberding doc: David Upatov
def show_points(coords, labels, ax, marker_size=375):
    pos_points = coords[labels == 1]
    neg_points = coords[labels == 0]
    ax.scatter(pos_points[:, 0], pos_points[:, 1], color='green',
               marker='*', s=marker_size, edgecolor='white', linewidth=1.25)
    ax.scatter(neg_points[:, 0], neg_points[:, 1], color='red',
               marker='*', s=marker_size, edgecolor='white', linewidth=1.25)


#TODO: 
#def bgremove5(myimage, color=(255, 255, 255), threshold=20):

#    new_img = np.zeros(myimage.shape, myimage.dtype)
#    mask_shape = (myimage.shape[0], myimage.shape[1])
#    mask = np.zeros(mask_shape, myimage.dtype)
#    for i in range(myimage.shape[0]):
#        for j in range(myimage.shape[1]):
#            if math.dist(myimage[i, j], color) > threshold:
#               new_img[i, j] = myimage[i, j]
#                mask[i, j] = 1
#    return new_img, mask
    


# Wendet eine Maske auf das Bild an und erzeugt ein neues Bild, das nur den maskierten Bereich enthält.
# Parameter:
# - img: Das ursprüngliche Bild.
# - masks: Die Maske, die auf das Bild angewendet wird.
# Gibt das neue Bild, die Größe des Bildausschnitts und die minimalen und maximalen Koordinaten des maskierten Bereichs zurück.
    #@auth: prog: Jokob Olberding doc: David Upatov
def applyMask(img, masks):
    new_img = []
    min_y, max_y, min_x, max_x = len(img), 0, len(img), 0
    for i in range(len(masks)):
        new_img.append([])
        for j in range(len(masks[i])):
            if i < min_y and masks[i][j] == 1:
                min_y = i
            if i > max_y and masks[i][j] == 1:
                max_y = i
            if j < min_x and masks[i][j] == 1:
                min_x = j
            if j > max_x and masks[i][j] == 1:
                max_x = j
            if masks[i][j] == 1:
                data = np.append(img[i][j], [255])
                new_img[i].append(data)
            else:
                new_img[i].append([0, 0, 0, 0])
                
    new_img = new_img[min_y:max_y]
    for i in range(len(new_img)):
        new_img[i] = new_img[i][min_x:max_x]
    new_img = np.array(new_img, dtype=np.uint8)
    size_box = new_img.shape[:2]
    return new_img, size_box, (min_y, max_y, min_x, max_x)