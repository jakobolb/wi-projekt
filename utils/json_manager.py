import json
import os

# Speichert die übergebenen Daten als JSON-Datei in einem definierten Workflow-Ordner.
# Parameter:
# - daten: Die zu speichernden Daten, erwartet ein Python-Dictionary oder eine ähnliche Datenstruktur.
# - wf_name: Der Name des Workflows, der als Dateiname für die JSON-Datei verwendet wird.
# @auth: David Upatov
def wf_speichern(wf_daten, wf_name):

    datei_name = wf_name + ".json"

    pfad = os.path.join(os.path.dirname(__file__),"..", "src", "Workflows", datei_name)

    with open(pfad, 'w') as json_datei:
        json.dump(wf_daten, json_datei, indent=4)
    print(f"Daten wurden in {pfad} gespeichert.")

# Liest eine JSON-Datei aus einem definierten Workflow-Ordner aus und gibt die Daten zurück.
# Parameter:
# - wf_name: Der Name des Workflows, dessen Daten gelesen werden sollen.
# Return:
# - daten: Die aus der JSON-Datei gelesenen Daten als Python-Dictionary.
# @auth: David Upatov
def wf_auslesen(wf_name):
    datei_name = wf_name + ".json"

    pfad = os.path.join(os.path.dirname(__file__),"..", "src", "Workflows", datei_name)

    with open(pfad, 'r') as json_datei:
        daten = json.load(json_datei)
    #print("Daten wurden aus der Datei gelesen:")
    return daten

# Speichert die übergebenen Daten als JSON-Datei in einem definierten LLM-Ordner.
# Parameter:
# - llm_daten: Die zu speichernden Daten, erwartet ein Python-Dictionary oder eine ähnliche Datenstruktur.
# - llm_name: Der Name des LLMs (Large Language Model), der als Dateiname für die JSON-Datei verwendet wird.
# @auth: David Upatov
def llm_speichern(llm_daten, llm_name):
    
    datei_name = llm_name + ".json"

    pfad = os.path.join(os.path.dirname(__file__),"..", "src", "LLMs", datei_name)

    with open(pfad, 'w') as json_datei:
        json.dump(llm_daten, json_datei, indent=4)

# Liest eine JSON-Datei aus einem definierten LLM-Ordner aus und gibt die Daten zurück.
# Parameter:
# - llm_option: Der Name des LLMs (Large Language Model), dessen Daten gelesen werden sollen.
# Return:
# - daten: Die aus der JSON-Datei gelesenen Daten als Python-Dictionary.
# @auth: David Upatov
def llm_auslesen(llm_option):
    datei_name = llm_option + ".json"

    pfad = os.path.join(os.path.dirname(__file__),"..", "src", "LLMs", datei_name)

    with open(pfad, 'r') as json_datei:
        daten = json.load(json_datei)
    #print("Daten wurden aus der Datei gelesen:")
    return daten


