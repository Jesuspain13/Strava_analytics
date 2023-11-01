import yaml
import os
import json


def load_yaml_config(filename='./config_local.yml'):
    print(f"Loading config file parameters {filename}...")
    with open(filename, 'r') as file:
        config: dict = yaml.safe_load(file)
    return config


def write_yaml_to_file(yaml_dict, filename='config_local.yml'):
    print(f"Saving as yaml in {filename}...")
    with open(f'{filename}', 'w', ) as f:
        yaml.dump(yaml_dict, f, sort_keys=False)
    print(f'Written to file {filename} OK')


def write_in_json(dict_to_write, filename='respuesta_activities.json'):
    print(f"Saving as json in {filename}...")
    with open(filename, 'w') as f:
        json.dump(dict_to_write, f)
