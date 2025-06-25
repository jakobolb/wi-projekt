import sqlite3
import io
from PIL import Image
import os


path = os.path.join(os.path.dirname(__file__),"..", "data", "wiprojekt.db")
#path = '/aliass/david/Documents/Code/pythoncode/WI-Projekt/wi-projekt-generative-ad/Mainbuild/Database/wiprojekt.db'

# Function to insert an entry into the Images table
def initiate_table():
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Images (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        alias TEXT NOT NULL,
        product TEXT NOT NULL,
        topics TEXT,
        prompts TEXT,
        dif_model TEXT,
        llm_option TEXT,
        image BLOB
    )
    ''')
    conn.commit()

initiate_table()

# Fügt einen neuen Eintrag in die Tabelle 'Images' ein.
# Parameter:
# - alias: Name des Benutzers, der das Bild hochgeladen hat
# - product: Name des Produkts, das mit dem Bild verbunden ist
# - topics: Verwendete Themen für die Bildgenerierung
# - prompts: Beschreibung des Bildes
# - dif_model: Modell, das zur Bildgenerierung verwendet wurde
# - llm_option: Verwendetes Sprachmodell
# - image: Das zu speichernde Bild als PIL Image-Objekt
#@auth: David Upatov & Jakob Olberding
    
def insert_image(alias, product, topics, prompts, dif_model, llm_option, image):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')  # Save the image to bytes in JPEG format
    image_bytes = image_bytes.getvalue()  # Get the bytes value
    # Insert the entry into the Images table
    cursor.execute("INSERT INTO Images (alias, product, topics, prompts, dif_model, llm_option, image) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (alias, product, topics, prompts, dif_model, llm_option, image_bytes))
    conn.commit()
    print("Image entry inserted successfully.")
    # Close the cursor and the connection
    cursor.close()
    conn.close()

# Ruft ein Bild anhand seiner ID aus der Datenbank ab.
# Parameter:
# - image_id: ID des abzurufenden Bildes
# Rückgabe:
# - Ein Dictionary mit Bildinformationen oder None, wenn kein Bild gefunden wurde.
#@auth: David Upatov & Jakob Olberding
def retrieve_image(image_id):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Images WHERE id = ?", (image_id,))
    image_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if image_data:
      images_info = []
      # Unpack the image data
      id, alias, product, topics, prompts, dif_model, llm_option, image_bytes = image_data
      # Convert image data from bytes to an image object
      image = Image.open(io.BytesIO(image_bytes))
      # Create a dictionary to store all data
      image_info = {
          "ID": id,
          "alias": alias,
          "Product": product,
          "Used Topics": topics,
          "prompts": prompts,
          "Image_gen Model": dif_model,
          "LLM Model": llm_option,
          "Image": image
      }
      images_info.append(image_info)
      return images_info
    else:
      print("No image found with the specified ID.")
      return None

# Ruft alle Bilder aus der Datenbank ab.
# Rückgabe:
# - Eine Liste von Dictionaries mit Bildinformationen oder None, wenn keine Bilder gefunden wurden.
# @auth: David Upatov & Jokab Olberding 
def get_all_images():
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Images")
    images_data = cursor.fetchall()

    if images_data:
        images_info = []  # Liste, um alle Bildinformationen zu speichern
        for image_data in images_data:
          # Unpack the image data
          id, alias, product, topics, prompts, dif_model, llm_option, image_bytes = image_data

          # Convert image data from bytes to an image object
          image = Image.open(io.BytesIO(image_bytes))

          # Create a dictionary to store all data
          image_info = {
              "ID": id,
              "alias": alias,
              "Product": product,
              "Used Topics": topics,
              "prompts": prompts,
              "Image_gen Model": dif_model,
              "LLM Model": llm_option,
              "Image": image
          }
          images_info.append(image_info)
        cursor.close()
        conn.close()
        return images_info
    else:
      print("No images found.")
      cursor.close()
      conn.close()
      return None

# Zeigt die Informationen eines oder mehrerer Bilder in der Konsole an.
# Parameter:
# - image_info_data: Entweder ein Dictionary für ein einzelnes Bild oder eine Liste von Dictionaries für mehrere Bilder.
# @auth: David Upatov & Jakob Olberding
def display_image_info(image_info_data):
    if isinstance(image_info_data, dict):  # Überprüfen, ob es sich um ein einzelnes Dictionary handelt
      print("Image ID:", image_info_data["ID"])
      print("alias:", image_info_data["alias"])
      print("Product:", image_info_data["Product"])
      print("Used Topics:", image_info_data["Used Topics"])
      print("prompts:", image_info_data["prompts"])
      print("Image_gen Model:", image_info_data["Image_gen Model"])
      print("LLM Model:", image_info_data["LLM Model"])
      display(image_info_data["Image"])
      print("")
      print("")
    elif isinstance(image_info_data, list):  # Überprüfen, ob es sich um eine Liste von Dictionaries handelt
        for image_info in image_info_data:
          print("Image ID:", image_info["ID"])
          print("alias:", image_info["alias"])
          print("Product:", image_info["Product"])
          print("Used Topics:", image_info["Used Topics"])
          print("prompts:", image_info["prompts"])
          print("Image_gen Model:", image_info["Image_gen Model"])
          print("LLM Model:", image_info["LLM Model"])
          display(image_info["Image"])
          print("")
          print("")
    else:
        print("Invalid input. Expected either a dictionary or a list of dictionaries.")


# Löscht ein Bild aus der Datenbank anhand seiner ID.
# Parameter:
# - entry_id: ID des zu löschenden Bildes
# @auth: Jakob Olberding
def delete_image(entry_id):
    conn = sqlite3.connect(path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Images WHERE id = ?", (entry_id,))
    image_data = cursor.fetchone()

    if image_data:
        cursor.execute("DELETE FROM Images WHERE id = ?", (entry_id,))
        conn.commit()
        print(f"Entry with ID {entry_id} deleted successfully.")
    else:
        print(f"No image found with ID {entry_id}.")

    # Close the cursor and the connection
    cursor.close()
    conn.close()