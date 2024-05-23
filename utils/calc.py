import pandas as pd
import numpy as np
from scipy.signal import find_peaks

"""
this_height = 0.3  # Grenze auf der y-Achse (0-1) 
this_prominence = 0.01 # [0.001 (mehr peaks) - 0.1 (weniger peaks)]
"""


def get_peak_df(dframe, this_height=0.3, this_prominence=0.01):
    df_peak = pd.DataFrame(columns=["Series", "Peak_Temperature", "Start_Temperature", "End_Temperature", "Area"])

    for col in list(dframe.columns):
        data = get_series_peaks_data(dframe, col, this_height, this_prominence)

        if df_peak.empty:
            df_peak = pd.DataFrame(data)
        else:
            df_peak = pd.concat([df_peak, pd.DataFrame(data)], ignore_index=True)

    return df_peak


def get_peak_df_for_searcharea(dframe, this_height=0.3, this_prominence=0.01, start=0, end=1):
    df_peak = pd.DataFrame(columns=["Series", "Peak_Temperature", "Start_Temperature", "End_Temperature", "Area"])
    dframe_area = dframe.loc[start:end]

    for col in list(dframe_area.columns):
        data = get_series_peaks_data_single(dframe_area, col, this_height, this_prominence)

        if df_peak.empty:
            df_peak = pd.DataFrame(data)
        else:
            df_peak = pd.concat([df_peak, pd.DataFrame(data)], ignore_index=True)

    return df_peak


def get_peak_df_by_searchareas(dframe, this_height=0.3, this_prominence=0.01, search_areas=None):
    df_peak = pd.DataFrame(columns=["Series", "Peak_Temperature", "Start_Temperature", "End_Temperature", "Area"])

    for area in search_areas:
        start = int(area["start"])
        end = int(area["end"])
        print(f"Start {start} to End {end}")
        dframe_area = dframe.loc[start:end]

        print(dframe_area.head())
        print(dframe_area.tail())
        print("______________________________________________________________________________")

        for col in list(dframe_area.columns):
            data = get_series_peaks_data_single(dframe_area, col, this_height, this_prominence)

            print("Data: ")
            print(data)
            print("______________________________________________________________________________")

            if df_peak.empty:
                df_peak = pd.DataFrame(data)
            else:
                df_peak = pd.concat([df_peak, pd.DataFrame(data)], ignore_index=True)

    return df_peak


def get_series_peaks_data_single(dframe, series_name, this_height=0.0, this_prominence=0.01,
                                 init_prominence=None, depth=0):
    if init_prominence is None:
        init_prominence = this_prominence

    print(f"depth: {depth}")
    data = get_series_peaks_data(dframe, series_name, this_height, this_prominence)

    max_prominence = abs(dframe[series_name].max() - dframe[series_name].min())

    # Abbruchkriterium
    if (this_prominence <= 0) or (depth == 20):
        return data

    count = len(data["Peak_Temperature"])
    if count == 0:
        next_prominence = this_prominence - init_prominence/10
        data = get_series_peaks_data_single(dframe, series_name, this_height, next_prominence,
                                            init_prominence, depth + 1)
    elif count > 1 and (this_prominence < max_prominence):
        next_prominence = this_prominence*1.3
        data = get_series_peaks_data_single(dframe, series_name, this_height, next_prominence,
                                            init_prominence, depth + 1)
    return data


def get_series_peaks_data(dframe, series_name, this_height=0.3, this_prominence=0.01):

    if "S3" in series_name:
        dframe = -dframe
        # Finden der Peaks
    peaks, properties = find_peaks(dframe[series_name], height=this_height, prominence=this_prominence, width=1)

    # Berechnung der ersten Ableitung der Daten -----------------------------
    first_derivative = np.diff(dframe[series_name])

    # Berechnung der zweiten Ableitung
    second_derivative = np.gradient(first_derivative)

    # Start- und Endpunkte bestimmen ----------------------------------------------------

    # Initialisierung der Listen für die Startpunkte -------------------
    start_points = []

    # Iteriere durch jeden Peak, um den Startpunkt zu bestimmen
    for peak_index in range(len(peaks)):
        peak = peaks[peak_index]
        # Suche rückwärts nach dem letzten Punkt, bei dem der 1. Ableitung negativ ist
        start = None
        for i in range(peak, 0, -1):  # ab peak rückwärts (theoretisch bis Anfang)
            if first_derivative[i - 1] < 0:
                start = i
                break
        if start is not None:
            start_points.append(start)
        else:
            start_points.append(0)

    # Initialisierung der Listen für die Endpunkte ----------------------
    end_points = []

    # Iteriere durch jeden Peak, um den Endpunkt zu bestimmen
    for peak_index in range(len(peaks)):
        peak = peaks[peak_index]
        # Suche vorwärts nach dem ersten Punkt, bei dem der 1. Ableitung positiv wird
        end = None
        for i in range(peak, len(first_derivative)):  # ab peak vorwärts (theoretisch bis Ende)
            if first_derivative[i] > 0:
                end = i + 1  # Berücksichtige np.diff Verschiebung
                break
        if end is not None:
            end_points.append(end)
        else:
            end_points.append(len(dframe) - 1)

    # Startpunkte optimieren ----------------------------------------------
    second_derivative_series = pd.Series(second_derivative)

    # Initialisierung von improved_start_points
    improved_start_points = []

    for i in range(len(start_points)):
        this_start = start_points[i]
        this_peak = peaks[i]

        # Eingrenzung der Series

        if len(list(range(this_start,
                          this_peak))) >= 3:  # Start mind. drei Indexpunkte entfernt vom Peak (Problem beim 3. Peak)
            second_der_area = second_derivative_series.loc[range(this_start, this_peak)]
        else:
            second_der_area = second_derivative_series.loc[range(this_start - 25, this_peak)]

        # Umgekehrte For-Schleife durch die Series UM die negativen Werte "am Peak" zu löschen
        for index in reversed(second_der_area.index):
            value = second_der_area[index]
            if value > 0.0001:
                break
            else:
                second_der_area = second_der_area.drop(index)

        new_start = this_start

        # Umgekehrte For-Schleife durch die Series
        # UM den Übergang ins Negative zu finden (mit Toleranz) bzw. erste sehr nach an der 0
        for index in reversed(second_der_area.index):
            value = second_der_area[index]
            new_start = index

            if value <= 0.0001:
                if dframe[series_name].iloc[index] < dframe[series_name].iloc[end_points[i]]:
                    break

        improved_start_points.append(new_start)

    # ---------------------
    if "S3" in series_name:
        dframe = -dframe

    peaks_temperature = dframe.index[peaks]
    # init_start_points_temperature = dframe.index[start_points]
    start_points_temperature = dframe.index[improved_start_points]
    end_points_temperature = dframe.index[end_points]

    return {"Series": series_name,
            'Peak_Temperature': peaks_temperature,
            'Start_Temperature': start_points_temperature,
            'End_Temperature': end_points_temperature,
            'Area': np.NaN}


def peak_df_area_calc(peak_dframe, measurement_dframe):
    for col in list(measurement_dframe.columns):
        area_calc(peak_dframe, measurement_dframe, col)


def area_calc(peak_dframe, measurement_dframe, series_name):
    areas = []
    for i, row in peak_dframe[peak_dframe["Series"] == series_name].iterrows():
        start_index = measurement_dframe.index.get_loc(row['Start_Temperature'])
        end_index = measurement_dframe.index.get_loc(row['End_Temperature'])

        this_x = measurement_dframe.index[start_index:end_index]

        # Bereich unterhalb des Peaks
        area_below_peak = np.trapz(measurement_dframe[series_name].iloc[start_index:end_index], x=this_x)

        # Bereich zwischen der Linie von Start- und Endpunkt und dem Bereich unterhalb des Peaks
        line_values = np.linspace(measurement_dframe[series_name].iloc[start_index],
                                  measurement_dframe[series_name].iloc[end_index], end_index - start_index)
        area_below_line = np.trapz(line_values, x=this_x)

        # Gesuchte Fläche (Integral bis zur Linie)
        total_area = area_below_peak - area_below_line
        areas.append(total_area)

    peak_dframe.loc[peak_dframe["Series"] == series_name, "Area"] = areas
    return True


def get_nearest_value(input_value, map_list):
    return min(map_list, key=lambda x: abs(x - input_value))
