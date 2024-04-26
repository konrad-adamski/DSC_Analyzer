import os
from flask import current_app
from models import Project
from utils.database import db


def delete_project(project_id: int):
    project = Project.query.get(project_id)

    if project:
        if project.ascii_file:
            delete_file(os.path.join(current_app.config['UPLOAD_FOLDER'], project.ascii_file))

        if project.info_csv:
            delete_file(os.path.join(current_app.config['UPLOAD_FOLDER'], project.info_csv))

        if project.measurements_csv:
            delete_file(os.path.join(current_app.config['UPLOAD_FOLDER'], project.measurements_csv))

        if project.peaks_csv:
            delete_file(os.path.join(current_app.config['UPLOAD_FOLDER'], project.peaks_csv))

        db.session.delete(project)
        db.session.commit()
        return True
    else:
        return False


def delete_file(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except OSError as e:
            print(f"Error beim Löschen der Datei: {e}")
            return False
        return True
    else:
        return False
