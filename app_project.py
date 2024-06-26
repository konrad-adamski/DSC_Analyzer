import json
import os

from flask import Blueprint, redirect, url_for, request, render_template, current_app
from werkzeug.utils import secure_filename

from config import load_default
from db_models import Project
from utils.calc import get_peak_df, peak_df_area_calc, get_peak_df_by_searchareas
from database import db
import pandas as pd

from utils.project_preparation import project_preparation
from utils.project_edit import delete_project

project_bp = Blueprint('project', __name__)


@project_bp.route('/projects_list/', methods=['GET', 'POST'])
def projects_list():
    projects = Project.query.all()
    print(type(projects))
    if not projects:
        return redirect(url_for('project.create_new_project'))
    return render_template("projects_list.html", projects=projects)


@project_bp.route('/new/', methods=['GET', 'POST'])
def create_new_project():
    context = {}

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

    return render_template('project_new.html', **context)


@project_bp.route('/<int:project_id>/', methods=['GET', 'POST'])
def project_overview(project_id):
    context = {"peak_max_numb": load_default("max_peak_numb")}

    project = Project.query.get(project_id)
    if project is None:
        return redirect(url_for('project.projects_list'))

    if request.method == "POST":
        if request.form.get('action'):

            if request.form.get("action") == "name_edit":
                name = request.form["project_name"]
                if name and name != "":
                    project.name = name
                    db.session.commit()

            elif request.form.get("action") == "delete_project":
                delete_project(project_id)
                return redirect(url_for('project.projects_list'))

            elif request.form.get("action") == "generate_peaks":
                measurement_csv_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.measurements_csv))
                df_measurement = pd.read_csv(measurement_csv_path, sep=";", index_col="Temp./°C")
                find_peak_height = request.form["project_find_peak_height"]
                find_peak_prominence = request.form["project_find_peak_prominence"]

                peak_count_select = request.form["peak_count_select"]


                # Bestimmung der Peaks
                if find_peak_height and find_peak_prominence:
                    if float(find_peak_height) > 0:
                        project.find_peak_height = find_peak_height
                    project.find_peak_prominence = find_peak_prominence
                    db.session.commit()

                    if peak_count_select == "All":
                        df_peak = get_peak_df(df_measurement,
                                              this_height=float(find_peak_height),
                                              this_prominence=float(find_peak_prominence))
                    else:
                        search_areas_json = json.loads(request.form["search_areas"])
                        df_peak = get_peak_df_by_searchareas(df_measurement,
                                                             this_height=float(find_peak_height),
                                                             this_prominence=float(find_peak_prominence),
                                                             search_areas=search_areas_json)

                else:
                    df_peak = get_peak_df(df_measurement)

                # Berechnung der Peak-Flächen
                info_csv_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.info_csv))
                df_info = pd.read_csv(info_csv_path, sep=";")
                print(df_info)

                peak_df_area_calc(df_peak, df_measurement, df_info)

                # Speichern
                peaks_csv_name = f"p{project.id}_peaks.csv"
                peaks_csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], peaks_csv_name)
                df_peak.to_csv(peaks_csv_path, sep=";", index=False)
                project.peaks_csv = peaks_csv_name
                db.session.commit()

    context["project"] = project
    return render_template('project_overview.html', **context)
