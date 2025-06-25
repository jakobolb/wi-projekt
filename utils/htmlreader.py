from bs4 import BeautifulSoup
import random

# Liest die Topics aus dem yout-topics.html Datei der Probanden
# @HTML: HTML-Datei aus der gelesen werden soll
# @auth: Jakob Ihler
def ListInterest(HTML):
  
  interests = []

  # Verwenden von Beautiful Soup, um den HTML-Inhalt zu parsen
  soup = BeautifulSoup(HTML, 'html.parser')

  # Extrahieren aller <div>-Tags, die Text enthalten
  all_divs = soup.find_all("div", string=True)

  # Iteration über alle Div-Tags; ersten beiden enthalten keine Interessen, alle werden doppelt genannt -> 2Steps; Hinzufügen zur Liste
  for div in all_divs[2::2]:
      interests.append(div.get_text(strip=True))

  return interests

# Sucht aus einer Liste i Objekte und gibt diese zureueck
# @topic_list: Liste aus der gewaehlt wird
# @i: Anzahl der Objekte die aus der Liste genommen werden
# @auth: David Upatov
def pick_random(topic_list, i):
    random_list = []
    for _ in range(i):
        random_object = random.choice(topic_list)

        print(topic_list)
        
        while random_object in random_list:
            random_object = random.choice(topic_list)
            
        print(random_object)
        random_list.append(random_object)
        if random_list == topic_list:
            break
        
    return random_list

# Schreibt Objekte einer Liste in ein String um 
def list_to_string (html_content):
    AdDataString =', '.join([str(item) for item in html_content])
    return AdDataString