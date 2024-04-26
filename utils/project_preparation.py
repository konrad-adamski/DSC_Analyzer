import os
import re
from io import StringIO

import numpy as np
import pandas as pd
from flask import current_app

from models import Project
from utils.database import db


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
    with open(file_path, "r") as datei:
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

    return info_df


# Measurement Dataframe ----------------------------------------------------------
def get_measurement_df(measurements_text, info_df):
    # Dataframe
    measurements_df = pd.read_csv(StringIO(measurements_text), sep=';', index_col=0)

    # 1) Anpassung der Spaltennamen
    num_cols = len(info_df)
    new_columns = [info_df.at[i, 'IDENTITY'] + '_' + info_df.at[i, 'SEGMENT'] for i in range(num_cols)]
    new_columns = [col.replace("/5", "") for col in new_columns]
    measurements_df.columns = new_columns

    # 2) Entfernung des Rauschens (Anfangs- und End-Werte)

    # ersten und letzten 25 Abschneiden
    measurements_df = measurements_df.iloc[25:-25]

    # 3) Entfernung des Initialisierungssegments (S1)
    columns_s1 = measurements_df.filter(like='_S1').columns

    measurements_df.drop(columns=columns_s1, inplace=True)
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
