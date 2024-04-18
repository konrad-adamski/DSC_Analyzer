import os
import pandas as pd
from io import StringIO

from flask import Flask, abort, request, render_template

from utils.calc import get_nearest_value, area_calc
from utils.template_tag import loop

app = Flask(__name__)
app.jinja_env.filters['loop'] = loop

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'

@app.route('/plot/<sample>/<segment>', methods=['GET', 'POST'])
def sample_segment_view(sample, segment):
    context = {}
    series = f"{sample}_{segment}"

    # Messwerte
    DATA_ROOT = os.path.join(app.root_path, 'data')
    measurement_csv_file_path = os.path.join(DATA_ROOT, 'measurement.csv')
    df_measurement = pd.read_csv(measurement_csv_file_path, sep=';', index_col=0)
    temperature_list = df_measurement.index.tolist()

    try:
        json_measurement = {"x": df_measurement.index.tolist(),
                            "y": df_measurement[series].tolist()}

    except Exception as err:
        print(f"KeyError beim Zugriff auf Spalte 'Series': {err}")
        abort(404)

    peak_csv_file_path = os.path.join(DATA_ROOT, 'peak.csv')
    df_peak_all = pd.read_csv(peak_csv_file_path, sep=';')

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
        df_peak.index = df_peak.index + 1  # Für Zuordnung im Plot
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
                area_calc(df_peak, df_measurement, series)  # anhand der neuen Punkte werden die Flächen berechnet

        json_peak = df_peak.to_json(orient="index", indent=4)
        print(df_peak)

    context["sample"] = sample
    context["segment"] = segment[1:]
    context["jsonPeak"] = json_peak
    context["peakCount"] = len(df_peak)
    context["jsonMeasurement"] = json_measurement
    return render_template('bokeh_plot.html', **context)

if __name__ == '__main__':
    app.run()
