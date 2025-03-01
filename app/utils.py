import json
import os

def load_json_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_json_file(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def get_user_history(username):
    history_file = f'history/{username}_history.json'
    return load_json_file(history_file)

def save_user_history(username, history_entry):
    history_file = f'history/{username}_history.json'
    history = load_json_file(history_file)
    history.append(history_entry)
    save_json_file(history_file, history)
