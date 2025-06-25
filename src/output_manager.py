import os
from PIL import Image


# Erstellt einen Ordner mit dem Aliasnamen und speichert ein uebergebenes Bild unter dem Bildnamen ab
# @image: Das zu speichernde Bild
# @directory_name: Aliasname nachdem der Ordner benannt ist indem das Bild gespeichert werden soll
# @image_name: Bildname
# @auth: David Upatov
def safe_image(image, directory_name, image_name):

    directory_name = "./output/" + directory_name

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    file_path = os.path.join(directory_name, image_name)
    image.save(file_path)
# Speichert ein Bild und dazugehörige Informationen in einem definierten Verzeichnis.
# Parameter:
# - image: Das zu speichernde Bild, erwartet ein Bildobjekt (z.B. aus PIL).
# - directory_name: Der Name des Verzeichnisses, in dem die Datei gespeichert werden soll.
# - image_name: Der Name der Bilddatei (z.B. "image.png").
# - txt_name: Der Name der Textdatei, in der die zusätzlichen Informationen gespeichert werden (z.B. "info.txt").
# - user: Benutzerinformationen, die in der Textdatei gespeichert werden sollen.
# - topics: Themen oder Kategorien, die dem Bild zugeordnet sind, werden in der Textdatei gespeichert.
# - ad_object: Das beworbene Objekt oder Produkt, das dem Bild zugeordnet ist.
# - clip: Ein CLIP-Score oder Ähnliches, der dem Bild zugeordnet ist.
# - aesthetic: Ein ästhetischer Wert, der dem Bild zugeordnet ist.
# @auth: David Upatov
def safe_image_and_info(image, directory_name, image_name, txt_name, user, topics, ad_object, clip, aesthetic):

    directory_name = "./output/" + directory_name

    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

    file_path = os.path.join(directory_name, image_name)
    image.save(file_path)

    info_path = os.path.join(directory_name, txt_name)
    with open(info_path, "w") as file:
        file.write("User: " + repr(user) + '\n')
        file.write("Topics: " + repr(topics) + '\n')
        file.write("Object: " + repr(ad_object) + '\n')
        file.write(repr(clip) + '\n')
        file.write(repr(aesthetic) + '\n')


