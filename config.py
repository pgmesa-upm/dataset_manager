
import os
import json
import shutil
from pathlib import Path

dir_ = Path(__file__).resolve().parent
env_path = dir_/'.env.json'
example_fname = '.env_example.json'

def config(key) -> any:
    if not os.path.exists(env_path):
        shutil.copy(dir_/example_fname, env_path)
    with open(env_path, 'r') as file:
        env_dict = json.load(file)
    return env_dict[key]