import os

from flask import Blueprint, redirect, url_for, request, render_template, current_app
from werkzeug.utils import secure_filename

from models import Project
from utils.database import db

project_bp = Blueprint('project', __name__)


@project_bp.route('/new', methods=['GET', 'POST'])
def create_new_project():
    if request.method == "POST":
        if request.form.get('name'):
            name = request.form["name"]
            new_project = Project(name=name)
        else:
            new_project = Project()
        db.session.add(new_project)
        db.session.commit()

        ascii_file = request.files['ascii_file']
        # ASCII-Datei speichern
        if ascii_file and allowed_textfile(ascii_file.filename):
            ascii_original_filename = secure_filename(ascii_file.filename)
            new_ascii_filename = f"p{new_project.id}_{ascii_original_filename}"

            # Datei speichern
            ascii_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_ascii_filename)
            ascii_file.save(ascii_file_path)

            # Dateipfad in der DB speichern
            ascii_file_url = url_for('data',
                                     filename='uploads/' + new_ascii_filename)  # URL für die hochgeladene Datei
            new_project.ascii_file = ascii_file_url
            # new_project.ascii_file = ascii_file_path

            db.session.commit()
        return redirect(url_for('hello_world'))

    return render_template('project_new.html')


def allowed_textfile(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() == 'txt'  # Erlaube nur bestimmte Dateiendungen

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in {'csv', 'txt'}  # Erlaube nur bestimmte Dateiendungen



@project_bp.route('/list')
def list_projects():
    return "Project List"


@project_bp.route('/edit')
def edit_project():
    return "New Project"


@project_bp.route('/delete/<int:project_id>')
def delete_project(project_id: int):
    project = Project.query.get(project_id)

    if project:
        if project.acii_file:
            try:
                os.remove(os.path.join(project_bp.root_path, project.acii_file[1:]))  # [1:] entfernt das führende Slash
            except OSError as e:
                print(f"Error beim Löschen der ASCII-Datei: {e}")
        if project.info_csv:
            try:
                os.remove(os.path.join(project_bp.root_path, project.info_csv[1:]))
            except OSError as e:
                print(f"Error beim Löschen der Info-CSV-Datei: {e}")

        if project.measurements_csv:
            try:
                os.remove(os.path.join(project_bp.root_path, project.measurements_csv[1:]))
            except OSError as e:
                print(f"Error beim Löschen der Measurements-CSV-Datei: {e}")
        if project.peaks_csv:
            try:
                os.remove(os.path.join(project_bp.root_path, project.peaks_csv[1:]))
            except OSError as e:
                print(f"Error beim Löschen der Peaks-CSV-Datei: {e}")

        db.session.delete(project)
        db.session.commit()
        return redirect(url_for('list_projects'))
    else:
        return "Project not found", 404
