import os
import pandas as pd
from io import StringIO
from flask import Blueprint, abort, request, render_template, redirect, url_for, current_app

from db_models import Project
from utils.calc import get_nearest_value, area_calc, get_peak_df, peak_df_area_calc, get_peak_df_for_searcharea

view_bp = Blueprint('view', __name__)


@view_bp.route('/project_<project_id>/', methods=['GET'])
def redirect_first(project_id):
    project = Project.query.get(project_id)
    print(project)
    if project:
        if project.measurements_csv:
            measurements_csv_file_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                                          project.measurements_csv))
            df_measurements = pd.read_csv(measurements_csv_file_path, sep=";", index_col=0)

            column_names = list(df_measurements.columns)
            first_series = column_names[0]
            sample, segment = first_series.split("_")

            return redirect(url_for("view.sample_segment_view", project_id=project_id, sample=sample, segment=segment))
        return redirect(url_for('project.project_overview', project_id=project_id))
    return redirect(url_for('project.create_new_project'))


@view_bp.route('/project_<project_id>/<sample>/<segment>', methods=['GET', 'POST'])
def sample_segment_view(project_id, sample, segment):
    context = {}
    project = Project.query.get(project_id)
    if project:
        if project.peaks_csv:
            series = f"{sample}_{segment}"

            # Messwerte
            measurement_csv_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.measurements_csv))
            df_measurement = pd.read_csv(measurement_csv_path, sep=";", index_col="Temp./°C")
            temperature_list = df_measurement.index.tolist()
            try:
                json_measurement = {"x": df_measurement.index.tolist(),
                                    "y": df_measurement[series].tolist()}
            except Exception as err:
                print(f"KeyError beim Zugriff auf Spalte 'Series': {err}")
                abort(404)
            print(project.peaks_csv)

            info_csv_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.info_csv))
            df_info = pd.read_csv(info_csv_path, sep=";")

            peaks_csv_file_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.peaks_csv))
            df_peak_all = pd.read_csv(peaks_csv_file_path, sep=';')

            df_peak = df_peak_all.loc[df_peak_all['Series'] == series]

            # current column_index
            column_index = df_measurement.columns.get_loc(series)
            has_previous = True if column_index > 0 else False
            has_next = True if column_index < len(df_measurement.columns) - 2 else False

            if has_previous:
                idx = column_index - 1
                previous_column = df_measurement.columns[idx]
                previous_sample, previous_segment = previous_column.split("_")
                context['previous_sample'] = previous_sample
                context['previous_segment'] = previous_segment

            if has_next:
                idx = column_index + 1
                next_column = df_measurement.columns[idx]
                next_sample, next_segment = next_column.split("_")
                context['next_sample'] = next_sample
                context['next_segment'] = next_segment

            # DataFrame in JSON konvertieren
            df_peak.reset_index(drop=True, inplace=True)
            df_peak.index += 1  # Für Zuordnung im Plot
            json_peak = df_peak.to_json(orient="index", indent=4)

            if request.method == 'POST':
                if request.form.get("action"):
                    jsonPeak_string = request.form.get('jsonPeak')
                    df_peak = pd.read_json(StringIO(jsonPeak_string), orient="index")

                    if request.form.get("action") == "plot_edit":  # die Punkte wurden verändert
                        onset_plausible = (df_peak['T1 (Onset) [°C]'] < df_peak['T_melt [°C]']).all()
                        offset_plausible = (df_peak['T2 (Offset) [°C]'] > df_peak['T_melt [°C]']).all()

                        if onset_plausible and offset_plausible:
                            # Neue Punkte zuweisen und neue Flächen berechnen
                            df_peak['T1 (Onset) [°C]'] = (
                                df_peak['T1 (Onset) [°C]'].apply(lambda x: get_nearest_value(x, temperature_list)))
                            df_peak['T2 (Offset) [°C]'] = (
                                df_peak['T2 (Offset) [°C]'].apply(lambda x: get_nearest_value(x, temperature_list)))
                            area_calc(df_peak, df_measurement, df_info,
                                      series)  # anhand der neuen Punkte werden die Flächen berechnet

                            update_peaks_csv(df_peak_all, df_peak, project, series)
                            json_peak = df_peak.to_json(orient="index", indent=4)

                    elif request.form.get("action") == "table_delete":
                        jsonPeak_string = request.form.get('jsonPeak')
                        df_peak = pd.read_json(StringIO(jsonPeak_string), orient="index")
                        df_peak.reset_index(drop=True, inplace=True)
                        df_peak.index += 1

                        update_peaks_csv(df_peak_all, df_peak, project, series)
                        json_peak = df_peak.to_json(orient="index", indent=4)

                    elif request.form.get("action") == "table_add":
                        min_temperature = float(request.form.get("min_temperature")) if request.form.get(
                            "min_temperature") else 0
                        max_temperature = float(request.form.get("max_temperature")) if request.form.get(
                            "max_temperature") else 300

                        min_temperature = get_nearest_value(min_temperature, temperature_list)
                        max_temperature = get_nearest_value(max_temperature, temperature_list)

                        df_peak_new = get_peak_df_for_searcharea(df_measurement.loc[:, [series]],
                                                                 this_height=0, this_prominence=0.01,
                                                                 start=min_temperature, end=max_temperature)

                        peak_df_area_calc(df_peak_new, df_measurement, df_info)
                        df_peak = add_new_peaks_to_df(df_peak, df_peak_new)

                        update_peaks_csv(df_peak_all, df_peak, project, series)
                        json_peak = df_peak.to_json(orient="index", indent=4)


            context["project_id"] = project_id
            context["sample"] = sample
            context["segment"] = segment[1:]
            context["jsonPeak"] = json_peak
            context["peakCount"] = len(df_peak)
            context["jsonMeasurement"] = json_measurement
            return render_template('bokeh_plot.html', **context)
        else:
            return redirect(url_for('project.project_overview', project_id=project.id))

    return redirect(url_for('project.create_new_project'))


def add_new_peaks_to_df(old_df, new_df):
    old_df = pd.concat([old_df, new_df], ignore_index=True)
    old_df.drop_duplicates(subset=['T_melt [°C]'], keep='first', inplace=True)
    old_df.sort_values(by=['T_melt [°C]'], inplace=True)
    old_df.reset_index(drop=True, inplace=True)
    old_df.index += 1
    return old_df


def update_peaks_csv(all_peaks_dframe, series_peaks_df, project, series):
    # Alte Werte löschen
    all_peaks_dframe = all_peaks_dframe.drop(all_peaks_dframe[all_peaks_dframe["Series"] == series].index)

    # Neue Werte einfügen
    all_peaks_dframe = pd.concat([all_peaks_dframe, series_peaks_df], ignore_index=True)

    # Temporäre Spalten für die Sortierung
    all_peaks_dframe["Sample_Numb"] = all_peaks_dframe['Series'].str.extract('(\d+)').astype(int)
    all_peaks_dframe['Segment'] = all_peaks_dframe['Series'].str.extract('_(S\d+)')  # Extrahiert dem Suffix

    # Sortieren des DataFrames zuerst nach Sample_Numb, dann Segment und zuletzt nach Peak_Temperature
    all_peaks_dframe = all_peaks_dframe.sort_values(by=['Sample_Numb', 'Segment', 'T_melt [°C]'])

    # Entfernen der temporären Spalten
    all_peaks_dframe.drop(columns=['Sample_Numb', 'Segment'], inplace=True)
    df_peak_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.peaks_csv))
    all_peaks_dframe.to_csv(df_peak_path, sep=";", index=False)

    return all_peaks_dframe
