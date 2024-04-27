# Verwende ein offizielles Python-Image als Basis
FROM python:3.11.6-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Anforderungen in den Container und installiere sie
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Kopiere den Rest des Codes in den Container
COPY . .


RUN rm -rf instance/*
RUN rm -rf data/*


# Öffne den Port, den dein Flask-Server benutzt
EXPOSE 5000

# Befehl, um den Flask-Server innerhalb des Containers zu starten
CMD ["python", "app.py"]
