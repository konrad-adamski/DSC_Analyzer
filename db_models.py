import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Importieren der ZoneInfo Klasse

from database import db


def load_default_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path_name = os.path.join(dir_path, 'config.json')
    with open(config_path_name, 'r') as file:
        data = json.load(file)
    return data['default']


default_config = load_default_config()


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    ascii_file = db.Column(db.String(255), nullable=True)
    info_csv = db.Column(db.String(255), nullable=True)
    measurements_csv = db.Column(db.String(255), nullable=True)
    peaks_csv = db.Column(db.String(255), nullable=True)
    find_peak_height = db.Column(db.Float, nullable=False, default=default_config['find_peak_height'])
    find_peak_prominence = db.Column(db.Float, nullable=False, default=default_config['find_peak_prominence'])
    date = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(ZoneInfo("Europe/Berlin")))

    def __repr__(self):
        if self.name:
            return f'{self.name}'
        else:
            return f'Project {self.id}'
