import os
import re
from io import StringIO

import numpy as np
import pandas as pd
from flask import current_app

from db_models import Project
from database import db


def project_preparation(project_id):
    project = Project.query.get(project_id)

    if project and project.ascii_file:
        try:
            # Split
            info_text, measurements_text = split_text(os.path.join(current_app.config['UPLOAD_FOLDER'],
                                                                   project.ascii_file))

            # Information Dataframe -----------------
            info_df = get_info_df(info_text)
            info_csv_name = f"p{project.id}_info.csv"
            info_csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], info_csv_name)

            info_df.to_csv(info_csv_path, sep=";", index=False)
            project.info_csv = info_csv_name

            # Commit in Database
            db.session.commit()

            # Measurement Dataframe -----------------
            measurements_df = get_measurement_df(measurements_text, info_df)
            measurements_csv_name = f"p{project.id}_measurements.csv"
            measurements_csv_path = os.path.join(current_app.config['UPLOAD_FOLDER'], measurements_csv_name)
            measurements_df.to_csv(measurements_csv_path, sep=";", index=True)
            project.measurements_csv = measurements_csv_name

            # Commit in Database
            db.session.commit()

        except Exception as e:
            return f"Error: {e}", 400
        return True

    else:
        return False


def split_text(file_path):
    with open(file_path, "r", encoding="ISO-8859-1") as datei:
        inhalt = datei.read()
    return inhalt.strip().split("##")  # returns info_text and measurement_text


# Information Dataframe ----------------------------------------------------------
def get_info_df(info_text):
    # 1) Aufteilung des Inhalts auf Key-List (Value) Paare
    raw_info_dict = key_entry_split(info_text)
    info_dict = entries_split(raw_info_dict)

    # 2) Allgemeine Bestimmung der Zeilen
    series_numb = len(info_dict["SAMPLE"])  # alternativ über IDENTITY

    # 3) Ausschluss der Keys mit wenig keys als series_numb
    key_value_count = count_entries_pro_key(info_dict)
    excluded_keys = [key for key, value in key_value_count.items() if value != series_numb]

    # 4) Dataframe bilden
    info_df = dict_to_dataframe(info_dict, ignore_keys=excluded_keys)

    # 5 Dataframe auf das Relevante (die wo mehr als 1 unique-Wert haben)
    unique_counts = info_df.nunique()
    series_relevant_columns = unique_counts[unique_counts > 1]
    info_df = info_df[series_relevant_columns.index.tolist()]

    # 6 Anpassung der Spaltennamen
    info_df.columns = info_df.columns.str.lower()
    info_df = info_df.rename(columns=replace_slash)

    # Konvertiere 'sample mass_mg' zu numerischen Werten, ignoriere Fehler
    info_df['sample mass_mg'] = pd.to_numeric(info_df['sample mass_mg'], errors='coerce')

    # Extrahieren der Heizrate
    info_df['heat_rate'] = info_df['range'].apply(extract_heat_rate)

    return info_df


# Measurement Dataframe ----------------------------------------------------------
def get_measurement_df(measurements_text, info_df):
    # Dataframe
    measurements_df = pd.read_csv(StringIO(measurements_text), sep=';', index_col=0)

    dsc_type = "unknown"
    if "mW/mg" in measurements_df.columns[0]:
        dsc_type = "mW/mg"
    elif "mW" in measurements_df.columns[0]:
        dsc_type = "mW"

    # 1) Anpassung der Spaltennamen
    num_cols = len(info_df)
    new_columns = [info_df.at[i, 'sample'] + '_' + info_df.at[i, 'segment'] for i in range(num_cols)]
    new_columns = [col.replace("/5", "") for col in new_columns]
    measurements_df.columns = new_columns

    # 2) Entfernung des Rauschens (Anfangs- und End-Werte)

    # ersten und letzten 25 Abschneiden
    measurements_df = measurements_df.iloc[25:-25]

    # 3) Entfernung des Initialisierungssegments (S1)
    columns_s1 = measurements_df.filter(like='_S1').columns

    measurements_df.drop(columns=columns_s1, inplace=True)

    # 4) Anpassung der Werte in mW

    measurements_df = measurements_df.apply(pd.to_numeric, errors='coerce')

    try:
        if dsc_type == "mW/mg":
            for column in measurements_df.columns:
                sample, _ = column.split('_')  # Sample und Segment ID extrahieren
                mass_mg_value = info_df.loc[info_df["sample"] == sample, "sample mass_mg"].iloc[0]
                measurements_df.loc[:, column] *= mass_mg_value
            dsc_type = "mW"

    except Exception as e:
        print(f"Error: {e}")

    # 5) Zeit-Spalte einfügen
    heating_rate_per_minute = info_df["heat_rate"][0]
    measurements_df['Time [sec]'] = get_time_from_temperatures(measurements_df, heating_rate_per_minute)

    return measurements_df


# Information Dataframe - Subfunktionen ------------------------------------------
# 1a) Einfache Key-Value Paare ----------------------------------
def key_entry_split(text):
    data = {}
    sections = text.strip().split("#")
    sections = sections[1:]  # erstes Element wird entfernt da leer (# ist am Anfang)
    for section in sections:
        key = section.split(":")[0]
        value_string = section.split(":")[1]
        data[key] = value_string.strip()
    return data


# 1b) Key-List Paare --------------------------------------------
# Aufteilung der Value-Strings in Value-Listen
def single_entry_split(text):
    return re.split(r'\s{2,}', text.strip())  # 2 oder mehrere Leerzeichen hintereinander


def entries_split(data):
    result = {}
    for key, value in data.items():
        result[key] = single_entry_split(value)
    return result


# 3) -------------------------------------------------------------
def count_entries_pro_key(dictionary):
    result = {}
    for key, values in dictionary.items():
        anzahl_der_values = len(values)
        result[key] = anzahl_der_values
    return result


# 4) Dataframe ---------------------------------------------------
def dict_to_dataframe(dictionary, ignore_keys=None):
    if ignore_keys is None:
        ignore_keys = []
    # Filtern der Schlüssel, die ignoriert werden sollen
    filtered_dict = {key: values for key, values in dictionary.items() if key not in ignore_keys}
    return pd.DataFrame(filtered_dict)


# Hilfsfunktionen ----------------------------------------------------

def replace_slash(column_name):
    return re.sub(r'\s*/\s*', '_', column_name.lower())

def extract_heat_rate(text):
    match = re.search(r'(\d+\.?\d*)(?=\(K/min\))', text)
    return float(match.group(1)) if match else None


def get_time_from_temperatures(df, heating_rate_per_minute=20):
    heating_rate_per_second = heating_rate_per_minute / 60
    start_temp = df.index[0]
    time_seconds = [(temp - start_temp) / heating_rate_per_second for temp in df.index]
    return time_seconds

