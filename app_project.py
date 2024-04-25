import os

from flask import Blueprint, redirect, url_for, request, render_template, current_app
from werkzeug.utils import secure_filename

from models import Project
from utils.calc import get_peak_df, peak_df_area_calc
from utils.database import db
import pandas as pd

from utils.project_preparation import get_info_df, split_text, get_measurement_df, project_preparation
from utils.project_edit import delete_project

project_bp = Blueprint('project', __name__)


@project_bp.route('/projects_list/', methods=['GET', 'POST'])
def projects_list():
    projects = Project.query.all()
    return render_template("projects_list.html", projects=projects)


@project_bp.route('/new/', methods=['GET', 'POST'])
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
        if ascii_file:
            ascii_original_filename = secure_filename(ascii_file.filename)
            new_ascii_filename = f"p{new_project.id}_{ascii_original_filename}"

            # Datei speichern
            ascii_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], new_ascii_filename)
            ascii_file.save(ascii_file_path)
            new_project.ascii_file = new_ascii_filename

            db.session.commit()

            # Preparation Process (Transformation)
            project_preparation(new_project.id)
            return redirect(url_for('project.project_overview', project_id=new_project.id))

    return render_template('project_new.html')


@project_bp.route('/<int:project_id>/', methods=['GET', 'POST'])
def project_overview(project_id):
    context = {}
    project = Project.query.get(project_id)

    if request.method == "POST":
        if request.form.get('action'):

            if request.form.get("action") == "name_edit":
                name = request.form["project_name"]
                if name and name != "":
                    project.name = name
                    db.session.commit()

            elif request.form.get("action") == "delete_project":
                delete_project(project_id)
                return redirect(url_for('hello_world'))

            elif request.form.get("action") == "generate_peaks":
                find_peak_height = request.form["project_find_peak_height"]
                find_peak_prominence = request.form["project_find_peak_prominence"]

                measurement_csv_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.measurements_csv))
                df_measurement = pd.read_csv(measurement_csv_path, sep=";", index_col="Temp./°C")

                # Bestimmung der Peaks
                if find_peak_height and find_peak_prominence:
                    df_peak = get_peak_df(df_measurement,
                                          this_height=float(find_peak_height),
                                          this_prominence=float(find_peak_prominence))
                    project.find_peak_height = find_peak_height
                    project.find_peak_prominence = find_peak_prominence
                    db.session.commit()
                else:
                    df_peak = get_peak_df(df_measurement)

                # Berechnung der Peak-Flächen
                peak_df_area_calc(df_peak, df_measurement)

                # Speichern
                peaks_csv_name = f"p{project.id}_peaks.csv"
                peaks_csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], peaks_csv_name)
                df_peak.to_csv(peaks_csv_path, sep=";", index=False)
                project.peaks_csv = peaks_csv_name
                db.session.commit()

    context["project"] = project
    return render_template('project_overview.html', **context)


