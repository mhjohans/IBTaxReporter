import os
from pathlib import Path


def get_output_folder():
    path_str = os.path.join(os.getcwd(), 'output/')
    Path(path_str).mkdir(exist_ok=True)
    return path_str


def get_csv_file(filename):
    return get_output_folder() + filename
