import numpy as np


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
