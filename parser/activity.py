import csv
from collections import defaultdict
from datetime import date, timedelta
from fractions import Fraction
from pathlib import Path

import pycountry


class ActivityFieldIds:
    statement_type = '#st'
    row_type = '#rt'
    amount = 'Amount'
    description = 'Description'
    date = 'Date'
    currency = 'Currency'


class Dividends:

    def __init__(self, country):
        self.country = country
        self.dividends = Fraction()
        self.withholding_taxes = Fraction()

    def __str__(self):
        def round_fraction(fraction):
            return round(float(fraction), 2)

        return self.country + ', ' + str(round_fraction(self.dividends)) + ', ' + str(
            round_fraction(self.withholding_taxes))

    def add_dividend(self, dividend):
        self.dividends += dividend

    def add_withholding_tax(self, withholding_tax):
        self.withholding_taxes += withholding_tax


def find_csv_file(location):
    """Searches for and returns the first CSV file located in the "input/activity" folder of the application"""
    activity_csv_files = list(Path(location).glob('*.csv'))
    if activity_csv_files:
        return activity_csv_files[0]
    else:
        raise FileNotFoundError('Activity CSV file not found!')


def parse_dividends(year=2018):
    csv_in = csv.DictReader(find_csv_file('../input/activity/').open(), fieldnames=[ActivityFieldIds.statement_type,
                                                                                    ActivityFieldIds.row_type])
    currency_rates = parse_currencies(year)
    dividends_by_ticker = {}
    for row in csv_in:
        if row.get(ActivityFieldIds.statement_type) == 'Dividends':
            if row.get(ActivityFieldIds.row_type) == 'Header':
                csv_in.fieldnames += row.get(None)
            elif row.get(ActivityFieldIds.description):
                description = row.get(ActivityFieldIds.description).split('(')
                ticker = description[0].strip()
                country_code = description[1][:2]
                country_code = country_code if country_code.isalpha() else 'US'
                country = pycountry.countries.get(alpha_2=country_code).name
                timestamp = date.fromisoformat(row.get(ActivityFieldIds.date))
                if timestamp.year != year:
                    continue
                currency = row.get(ActivityFieldIds.currency)
                amount = Fraction(row.get(ActivityFieldIds.amount))
                while not currency_rates[currency].get(timestamp):
                    timestamp -= timedelta(days=1)
                amount_in_base_currency = amount / currency_rates[currency][timestamp]
                dividends = dividends_by_ticker.setdefault(ticker, Dividends(country))
                dividends.add_dividend(amount_in_base_currency)
    sum_of_dividends = Fraction()
    for ticker, dividends in dividends_by_ticker.items():
        print(ticker, dividends)
        sum_of_dividends += dividends.dividends
    print('\nTotal sum of dividends', round(float(sum_of_dividends), 2))


def parse_currencies(year):
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
