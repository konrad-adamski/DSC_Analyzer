# Verwenden Sie ein offizielles Python-Laufzeit-Image als Eltern-Image
FROM python:3.11.8-slim

# Arbeitsverzeichnis im Container festlegen
WORKDIR /app

# Abhängigkeiten installieren
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Kopieren des aktuellen Verzeichnisses in das Arbeitsverzeichnis im Container
COPY . .

# Ausnahme für den data Ordner
# (nicht nötig, aber erhöht die Klarheit, falls das Dockerfile alleine betrachtet wird)
RUN rm -rf /app/data

# Der Port, auf dem die Anwendung laufen wird
EXPOSE 5000

# Befehl zum Starten der Anwendung
CMD ["flask", "run", "--host=0.0.0.0"]
