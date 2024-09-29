import os
import json

config = {}

def load_config():
    global config
    dir_path = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(dir_path, "config.json")

    try:
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print(f"configuration file '{config_file_path}'' not found.")
        return None  # file doesnt exist
    except json.JSONDecodeError:
        print(f"error decoding JSON from the configuration file '{config_file_path}'.")
        return None  # bad json
    
def save_config(config):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(dir_path + "/config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)