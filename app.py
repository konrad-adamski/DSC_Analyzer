import os

from flask import Flask, send_from_directory
from app_peak import peak_bp
from app_project import project_bp
from utils.database import init_db
from utils.template_tag import loop

app = Flask(__name__)
app.jinja_env.filters['loop'] = loop

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurationen für den Datei-Upload
app.config['UPLOAD_FOLDER'] = 'data/uploads'  # Stelle sicher, dass dieser Pfad existiert
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Optional: Maximale Dateigröße (z.B. 16 MB)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

init_db(app)  # Initialisiert die Datenbank mit der Konfiguration von Flask

app.register_blueprint(project_bp, url_prefix='/project')
app.register_blueprint(peak_bp, url_prefix='/peak')


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


# für href="{{ url_for('data', filename='measurement.csv') }}" bzw. Download
@app.route('/data/<path:filename>')
def data(filename):
    return send_from_directory('data', filename)


if __name__ == '__main__':
    app.run()
