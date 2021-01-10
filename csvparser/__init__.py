import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup

stock_names_by_ticker = {}


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


def scrape_stock_name(ticker):
    if ticker in stock_names_by_ticker:
        return stock_names_by_ticker.get(ticker)
    else:
        name = 'N/A'
        result = requests.get('https://finance.yahoo.com/quote/' + ticker)
        if result.ok:
            page_content = result.text
            soup = BeautifulSoup(page_content, features='lxml')
            name_tag = soup.find('h1')
            if name_tag:
                ticker_and_name = name_tag.text
                ticker_divider_index = ticker_and_name.find('-')
                if ticker_divider_index != -1:
                    scraped_name = ticker_and_name[ticker_divider_index + 2:]
                    if scraped_name and not scraped_name.isnumeric():
                        name = scraped_name
        stock_names_by_ticker[ticker] = name
        return name
