import os

from flask import Flask, send_from_directory, redirect, url_for, send_file, jsonify, request
from werkzeug.utils import secure_filename

from app_view import view_bp
from app_project import project_bp
from db_models import Project
from database import init_db
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


@app.route('/download_excel/<int:project_id>/<string:attribute>/<string:filename>/')
def download_excel(project_id, attribute, filename):
    sample = request.args.get('sample')
    segment = request.args.get('segment')

    project = Project.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404

    attr_value = getattr(project, attribute, None)
    if not attr_value:
        return jsonify({'error': 'Attribute not found'}), 404

    file_path = str(os.path.join(app.config['UPLOAD_FOLDER'], attr_value))
    df = pd.read_csv(file_path, sep=';')

    if attribute == "peaks_csv":
        df[['Sample', 'Segment']] = df['Series'].str.split('_', expand=True)
        column_order = (['File', 'Series', 'Sample', 'Segment']
                        + [col for col in df.columns if col not in ['File', 'Series', 'Sample', 'Segment']])
        df = df[column_order]

    if sample and segment:
        series = sample + '_S' + segment
        print(series)

        if attribute == "peaks_csv":
            df = df[df["Series"] == series]
        elif attribute == "measurements_csv":
            df = df[[series]]
    sheet_name = str(attribute).split('_')[0]

    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        add_to_excel(df, writer, sheet_name)
    output.seek(0)

    # Sicherstellen, dass der Dateiname sicher ist (keine ungültigen Zeichen enthält)
    safe_filename = secure_filename(filename)
    return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                     as_attachment=True, download_name=safe_filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
