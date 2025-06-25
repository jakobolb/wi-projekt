# Wi-Projekt Generative Ad

## Umgebungsvariablen
Um das Streamlit-Frontend dieses Repositories nutzen zu können, müssen die folgenden Umgebungsvariablen in der Datei Mainbuild/.env gesetzt werden:
```bash
nano .env
```

```bash
OPENAI_API_KEY=
HUGGINGFACE_API=
```
Da Streamlit seine eigene Umgebung aufbaut, kann nicht direkt auf die Umgebungsvariablen der Host-Umgebung zugegriffen werden. Falls die Module unabhängig von Streamlit genutzt werden sollen, müssen die entsprechenden Umgebungsvariablen in der Host-Umgebung gesetzt werden.

## Quickstart
Um das Projekt zu starten, installiere zunächst die benötigten Python-Bibliotheken:

```bash
pip install -r requirements.txt
```

### Für Windows Nutzer
Sollte Windows benutzt werden bitte sicherstellen, ob das richtigre torch/pytorch installiert ist
```bash
pip uninstall torch torchvision torchaudio
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
### Starten der UI

Starte die UI mit Streamlit durch Ausführen des Skripts st_main.py:

```bash
streamlit run st_main.py
```
Streamlit öffnet dann die UI in deinem Standardbrowser und macht sie über einen Port des Localhost (z.B. http://localhost:8501) zugänglich.

## Cuda anstatt MPS

Alle Module prüfen automatisch, ob CUDA- oder MPS-Treiber verfügbar sind, und laden die Modelle entsprechend darauf.

## Output

Die generierten Bilder werden im Verzeichnis ./Mainbuild/output/ALIAS gespeichert, wobei ALIAS der Alias des Probanden ist.
```bash
cd output
```

## Werbedaten

Die Werbedaten welche während des WI-Projekts gesammelt und Pseudomisiert wurden findet man im folgenden Pfad:
```bash
cd Werbedaten
```


## Huggingface Cache von Modellen befreien

Um den Huggingface-Cache zu bereinigen, stelle sicher, dass das huggingface_hub["cli"] installiert ist:


```bash 
pip install huggingface_hub["cli"]
```
Führe dann den folgenden Befehl im Terminal aus:

```bash
huggingface-cli delete-cache
```
Es öffnet sich ein Menü, das alle im Huggingface-Cache gespeicherten Modelle anzeigt. Mit den Pfeiltasten navigierst du und mit der Leertaste markierst du die Modelle, die gelöscht werden sollen. Bestätige den Löschvorgang mit "Enter".

## How-To
Im Folgenden wird erläutert, wie das Frontend verwendet wird.

### Create Workflow
Ein Workflow definiert die Pipeline zur Erstellung der Werbebilder. Folgende Konfigurationen können vorgenommen werden:

- Workflow-Bezeichnung: Name des Workflows, der später in der Auswahl angezeigt wird.
- Pfad des ersten Diffusor-Modells: Huggingface-Pfad für das erste Diffusor-Modell.
- Pfad des zweiten Diffusor-Modells: Huggingface-Pfad für das zweite Diffusor-Modell.
- Pfad des dritten Diffusor-Modells: Huggingface-Pfad für das dritte Diffusor-Modell.
- LLM-System-Prompt: Optionales System-Prompt. Standardmäßig wird das während des Projekts erstellte System-Prompt verwendet:
```bash
You are an art director who uses an image-generating \ AI to create advertisment images for a specific product. In order for the AI to generate good images,          you use the following pattern: An image, with no people, of [product] [adjective] [subject] [doing action], [creative lighting style], detailed, realistic, trending on artstation, in style of [advertisment image style]
```
- Standard-Negativprompts: Bekannte Negativprompts aus Literatur und Foren, um unförmige Bildgenerierungen zu vermeiden.
- Negative Embeddings: Setzt die Vektorsammlung "bad_prompt_version2" ein, um unförmige Bilder zu vermeiden (nicht mit jedem Modell kompatibel).
- Prompt-Evaluation: Lädt das LLM-Modell pai-bloom-1b1-text2prompt-sd-v2, um Prompts für Bildgenerierungs-KIs besser lesbar zu machen (vom Projektteam jedoch verworfen).
- CLIP-Score: Evaluationstool zur Überprüfung, wie genau das generierte Bild den Tokens im Prompt entspricht.
- CLIP-Score-Grenzwert: Mindestwert des CLIP-Scores, der erreicht werden muss, damit das Modell das Bild akzeptiert (Standardwert 30 basierend auf Projekterfahrung).
- Ästhetik-Score: Evaluationstool zur Überprüfung der Bildverformung. Je höher der Wert, desto weniger verformt ist das Bild.

## Add LLM

Mit "Add LLM" kann ein LLM-Modell aus Huggingface ausgewählt werden, das zur Generierung der Input-Prompts verwendet wird.

- Huggingface-Pfad des LLM: Huggingface-Pfad für das zu verwendende LLM.

## Generieren von Werbebilde

Wähle ein zuvor hinzugefügtes LLM und einen erstellten Workflow aus. Mit "delete workflow" kannst du den ausgewählten Workflow löschen. LLMs können gelöscht werden, indem der Huggingface-Cache wie oben beschrieben geleert wird und der Verweis auf das Modell im Verzeichnis Mainbuild/src/LLMs entfernt wird.

Unter "Details" kannst du jede Konfiguration von LLM und Workflow einsehen.

Personen-Alias: Ein Alias oder eine ID, die auf den Probanden verweist.
Werbeobjekt: Das Objekt, das in den Bildern beworben werden soll.

Lade eine my_topics.html-Datei des Probanden per Drag & Drop oder über die Dateisuche hoch. Diese Datei kann jeder Nutzer über Instagram anfordern. Da sich der Vorgang zur Beschaffung dieser Daten häufig ändert, wird empfohlen, eine aktuelle Anleitung online zu suchen.

Nachdem das LLM und der Workflow ausgewählt sowie Alias und Objekt definiert wurden, und die Werbedaten hochgeladen sind, kann mit "Generate Advertisements" die Pipeline zur Generierung von drei Werbebildern basierend auf den Werbedaten gestartet werden.

## Gpt Whitelist
Die GPT-Whitelist sind Namen von openAI Modellen, welche anstelle eines Huggingface-Pfades angegeben werden können um openAI Modelle in entsprechenden Abschnitten zu nutzen.

```bash
gpt_whitelist = ["gpt-4", "gpt-4o", "gpt-3.5-turbo", "dall-e-2", "dall-e-3"]
```
