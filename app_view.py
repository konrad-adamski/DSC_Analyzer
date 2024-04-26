import os
import pandas as pd
from io import StringIO
from flask import Blueprint, abort, request, render_template, redirect, url_for, current_app

from models import Project
from utils.calc import get_nearest_value, area_calc, get_peak_df, peak_df_area_calc

view_bp = Blueprint('view', __name__)


@view_bp.route('/project_<project_id>/', methods=['GET'])
def redirect_first(project_id):
    project = Project.query.get(project_id)
    if project:
        if project.peaks_csv:
            peaks_csv_file_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.peaks_csv))
            df_peak_all = pd.read_csv(peaks_csv_file_path, sep=';')
            series = df_peak_all.loc[0, "Series"]
            sample, segment = series.split("_")
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

            peaks_csv_file_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.peaks_csv))
            df_peak_all = pd.read_csv(peaks_csv_file_path, sep=';')

            df_peak = df_peak_all.loc[df_peak_all['Series'] == series]

            # previous & next
            rows_previous = df_peak.index.min() > 0
            rows_next = df_peak.index.max() < df_peak_all.index.max()

            if rows_previous:
                idx = df_peak.index.min() - 1
                previous_sample, previous_segment = df_peak_all["Series"].iloc[idx].split('_')
                context['previous_sample'] = previous_sample
                context['previous_segment'] = previous_segment
                print(previous_sample)
            if rows_next:
                idx = df_peak.index.max() + 1
                next_sample, next_segment = df_peak_all["Series"].iloc[idx].split('_')
                context['next_sample'] = next_sample
                context['next_segment'] = next_segment

            if request.method == 'GET':
                # DataFrame in JSON konvertieren
                df_peak.reset_index(drop=True, inplace=True)
                df_peak.index += 1  # Für Zuordnung im Plot
                json_peak = df_peak.to_json(orient="index", indent=4)
                print(df_peak)
                print(json_peak)

            else:  # request.method == 'POST':
                jsonPeak_string = request.form.get('jsonPeak')
                df_peak = pd.read_json(StringIO(jsonPeak_string), orient="index")

                if request.form.get("action"):
                    if request.form.get("action") == "plot_edit":  # die Punkte wurden verändert
                        # Neue Punkte zuweisen und neue Flächen berechnen
                        df_peak['Start_Temperature'] = (df_peak['Start_Temperature']
                                                        .apply(lambda x: get_nearest_value(x, temperature_list)))
                        df_peak['End_Temperature'] = (df_peak['End_Temperature']
                                                      .apply(lambda x: get_nearest_value(x, temperature_list)))
                        area_calc(df_peak, df_measurement,
                                  series)  # anhand der neuen Punkte werden die Flächen berechnet
                    elif request.form.get("action") == "table_delete":
                        df_peak.reset_index(drop=True, inplace=True)
                        df_peak.index += 1

                    elif request.form.get("action") == "table_add":
                        min_temperature = float(request.form.get("min_temperature")) if request.form.get(
                            "min_temperature") else 0
                        max_temperature = float(request.form.get("max_temperature")) if request.form.get(
                            "max_temperature") else 300

                        min_temperature = get_nearest_value(min_temperature, temperature_list)
                        max_temperature = get_nearest_value(max_temperature, temperature_list)

                        df_peak_new = get_peak_df(df_measurement.loc[min_temperature:max_temperature, [series]],
                                                  this_height=0, this_prominence=0.0001)

                        peak_df_area_calc(df_peak_new, df_measurement)
                        df_peak = add_new_peaks_to_df(df_peak, df_peak_new)

                    update_peaks_csv(df_peak_all, df_peak, project)

                json_peak = df_peak.to_json(orient="index", indent=4)
                print(df_peak)

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
    old_df.drop_duplicates(subset=['Peak_Temperature'], keep='first', inplace=True)
    old_df.sort_values(by=['Peak_Temperature'], inplace=True)
    old_df.reset_index(drop=True, inplace=True)
    old_df.index += 1
    return old_df


def update_peaks_csv(all_peaks_dframe, series_peaks_df, project):

    # Werte zusammenführen
    all_peaks_dframe = pd.concat([all_peaks_dframe, series_peaks_df], ignore_index=True)

    # neue Werte behalten
    all_peaks_dframe.drop_duplicates(subset=['Series', 'Peak_Temperature'], keep='last', inplace=True)

    # Temporäre Spalten für die Sortierung
    all_peaks_dframe["Sample_Numb"] = all_peaks_dframe['Series'].str.extract('(\d+)').astype(int)
    all_peaks_dframe['Segment'] = all_peaks_dframe['Series'].str.extract('_(S\d+)')  # Extrahiert den Suffix

    # Sortieren des DataFrames zuerst nach Sample_Numb, dann Segment und zuletzt nach Peak_Temperature
    all_peaks_dframe = all_peaks_dframe.sort_values(by=['Sample_Numb', 'Segment', 'Peak_Temperature'])

    # Entfernen der temporären Spalten
    all_peaks_dframe.drop(columns=['Sample_Numb', 'Segment'], inplace=True)
    df_peak_path = str(os.path.join(current_app.config['UPLOAD_FOLDER'], project.peaks_csv))
    all_peaks_dframe.to_csv(df_peak_path, sep=";", index=False)

    return all_peaks_dframe

