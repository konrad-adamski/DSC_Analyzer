import json
import os


def load_default_config():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path_name = os.path.join(dir_path, 'config.json')
    with open(config_path_name, 'r') as file:
        data = json.load(file)
    return data['default']


def load_default(val):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_path_name = os.path.join(dir_path, 'config.json')
    with open(config_path_name, 'r') as file:
        data = json.load(file)
    return data['default'][val]




