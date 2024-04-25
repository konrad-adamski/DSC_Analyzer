import os

from flask import Flask, send_from_directory, redirect, url_for, send_file
from app_view import view_bp
from app_project import project_bp
from utils.database import init_db
from utils.template_tag import loop, loop_max3

import pandas as pd
from io import BytesIO

from utils.xlsx_functions import add_to_excel

app = Flask(__name__)
app.jinja_env.filters['loop'] = loop
app.jinja_env.filters['loop_max3'] = loop_max3

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Konfigurationen für den Datei-Upload
app.config['UPLOAD_FOLDER'] = 'data'  # Stelle sicher, dass dieser Pfad existiert
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024  # Optional: Maximale Dateigröße (z.B. 1 MB)

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

init_db(app)  # Initialisiert die Datenbank mit der Konfiguration von Flask

app.register_blueprint(project_bp, url_prefix='')
app.register_blueprint(view_bp, url_prefix='/view')


@app.route('/')
def index():
    return redirect(url_for('project.projects_list'))


@app.route('/data/<path:filename>')
def data(filename):
    return send_from_directory('data', filename)


@app.route('/download_excel')
def download_excel():
    # Erstelle ein DataFrame als Beispiel
    data = {'Number': [1, 2, 3], 'Amount': [50.0, 20.5, 31.75], 'Description': ['A', 'B', 'C']}
    df = pd.DataFrame(data)

    # Erstelle eine BytesIO-Instanz, um die Datei im Speicher zu speichern
    output = BytesIO()

    # Erstelle einen Pandas Excel writer mit XlsxWriter als Engine und speichere in BytesIO
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        add_to_excel(df, writer)
        #writer.save()
        #writer.book.close()

    # Gehe zum Anfang des BytesIO-Stream, um die Datei zu senden
    output.seek(0)

    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name='download.xlsx')


if __name__ == '__main__':
    app.run()
