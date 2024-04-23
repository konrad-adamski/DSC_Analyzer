from datetime import datetime
from zoneinfo import ZoneInfo  # Importieren der ZoneInfo Klasse

from utils.database import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    ascii_file = db.Column(db.String(255), nullable=True)
    info_csv = db.Column(db.String(255), nullable=True)
    measurements_csv = db.Column(db.String(255), nullable=True)
    peaks_csv = db.Column(db.String(255), nullable=True)
    date = db.Column(db.DateTime, nullable=True, default=lambda: datetime.now(ZoneInfo("Europe/Berlin")))

    def __repr__(self):
        if self.name:
            return f'{self.name}'
        else:
            return f'Project {self.id}'
