import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal

import csvparser


def parse_currencies(year):
    currencies = ['EUR', 'USD', 'CAD', 'GBP', 'SEK']
    csv_in = csv.DictReader(csvparser.find_csv_file(csvparser.get_input_folder('currency')).open())
    daily_rate_by_currency = defaultdict(dict)
    for row in csv_in:
        timestamp = date.fromisoformat(row.get('Date'))
        if year - 1 <= timestamp.year <= year + 1:
            for currency in currencies:
                rate = Decimal(row.get(currency)) if currency != 'EUR' else Decimal(1)
                daily_rate_by_currency[currency][timestamp] = rate
    return daily_rate_by_currency
