import os
from pathlib import Path


def get_input_folder(sub_folder):
    path_str = os.path.join(os.getcwd(), 'input/' + sub_folder)
    Path(path_str).mkdir(parents=True, exist_ok=True)
    return path_str


def find_csv_file(path):
    """Searches for and returns the first CSV file located inside the folder marked by the given path."""
    activity_csv_files = list(Path(path).glob('*.csv'))
    if activity_csv_files:
        return activity_csv_files[0]
    else:
        raise FileNotFoundError('CSV file not found!')
