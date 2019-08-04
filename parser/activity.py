import csv
from collections import defaultdict
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path


class ActivityFieldIds:
    statement_type = '#st'
    row_type = '#rt'
    amount = 'Amount'
    description = 'Description'
    date = 'Date'
    currency = 'Currency'


def find_csv_file(location):
    """Searches for and returns the first CSV file located in the "input/activity" folder of the application"""
    activity_csv_files = list(Path(location).glob('*.csv'))
    if activity_csv_files:
        return activity_csv_files[0]
    else:
        raise FileNotFoundError('Activity CSV file not found!')


def parse_dividends():
    csv_in = csv.DictReader(find_csv_file('../input/activity/').open(), fieldnames=[ActivityFieldIds.statement_type,
                                                                                    ActivityFieldIds.row_type])
    currency_rates = parse_currencies()
    dividends_by_ticker = defaultdict(Fraction)
    for row in csv_in:
        if row.get(ActivityFieldIds.statement_type) == 'Dividends':
            if row.get(ActivityFieldIds.row_type) == 'Header':
                csv_in.fieldnames += row.get(None)
            elif row.get(ActivityFieldIds.description):
                ticker = row.get(ActivityFieldIds.description).split('(')[0].strip()
                timestamp = date.fromisoformat(row.get(ActivityFieldIds.date))
                currency = row.get(ActivityFieldIds.currency)
                amount = Fraction(row.get(ActivityFieldIds.amount))
                while not currency_rates[currency].get(timestamp):
                    timestamp -= timedelta(days=1)
                amount_in_base_currency = amount / currency_rates[currency][timestamp]
                dividends_by_ticker[ticker] += amount_in_base_currency
    sum_of_dividends = Fraction()
    for ticker, dividend in dividends_by_ticker.items():
        print(ticker, round(float(dividend), 2))
        sum_of_dividends += dividend
    print('\nTotal sum of dividends', round(float(sum_of_dividends), 2))


def parse_currencies(year=2018):
    currencies = ['EUR', 'USD', 'CAD', 'GBP', 'SEK']
    csv_in = csv.DictReader(find_csv_file('../input/currency/').open())
    daily_rate_by_currency = defaultdict(dict)
    for row in csv_in:
        timestamp = date.fromisoformat(row.get('Date'))
        if year - 1 <= timestamp.year <= year + 1:
            for currency in currencies:
                rate = Fraction(row.get(currency)) if currency != 'EUR' else Fraction(1)
                daily_rate_by_currency[currency][timestamp] = rate
    return daily_rate_by_currency


parse_dividends()
