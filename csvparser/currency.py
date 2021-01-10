import csv
from collections import defaultdict
from datetime import date
from decimal import Decimal
from enum import Enum

import csvparser


class CurrencyTimeFrame(Enum):
    DAILY = 1
    ANNUAL = 2


def parse_currencies(year, time_frame):
    currencies = ['EUR', 'USD', 'CAD', 'GBP', 'SEK']
    if time_frame == CurrencyTimeFrame.DAILY:
        csv_in = csv.DictReader(csvparser.find_csv_file(csvparser.get_input_folder('currency')).open())
        daily_rate_by_currency = defaultdict(dict)
        for row in csv_in:
            timestamp = date.fromisoformat(row.get('Date'))
            if year - 1 <= timestamp.year <= year + 1:
                for currency in currencies:
                    rate = Decimal(row.get(currency)) if currency != 'EUR' else Decimal(1)
                    daily_rate_by_currency[currency][timestamp] = rate
        return daily_rate_by_currency
    else:
        return {'EUR': Decimal(1), 'USD': Decimal('1.1195'), 'CAD': Decimal('1.4855')}
