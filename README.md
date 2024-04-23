# Lokal
- Holen Sie alle Daten aus der Repository.
- Installieren Sie alle nötige Pakete: "pip install -r requirements.txt"
- Starten Sie die Anwendung mit "python app.py"
- über http://127.0.0.1:5000 können Sie auf die App zugreifen.
- Über http://127.0.0.1:5000/view/project_4/C5/S5 können Sie auf dem Beispieldatensatz zugreifen.

# Docker
- Laden Sie die docker-compose.yml herunter!
- Im gleichen Ordner erstellen Sie einen Daten-Ordner und legen dort "measurement.csv" & "peak.csv" ab. Die Daten liegen im "data"-Ordner in der Repository.
- Passen Sie in der docker-compose.yml <your_data_folder> durch ihren Daten-Ordner an!
- Führen Sie: "docker-compose up"
- über http://127.0.0.1:8000 können Sie auf die App zugreifen.
- Über http://127.0.0.1:8000/plot/C1/S5 können Sie auf dem Beispieldatensatz zugreifen.



## Pakete
- pip install scipy



