import csv
import gettext
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

    def __init__(self, ticker, country):
        self.ticker = ticker
        self.country = country
        self.dividends = Fraction()
        self.dividends_float = 0
        self.withholding_taxes = Fraction()
        self.withholding_taxes_float = 0

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.ticker, self.country, self.dividends_float, self.withholding_taxes_float)

    def add_dividend(self, dividend):
        self.dividends += dividend
        self.dividends_float = round_fraction(self.dividends)

    def add_withholding_tax(self, withholding_tax):
        self.withholding_taxes += withholding_tax
        self.withholding_taxes_float = round_fraction(self.withholding_taxes)


def round_fraction(fraction):
    return round(float(fraction), 2)


def find_csv_file(location):
    """Searches for and returns the first CSV file located in the "input/activity" folder of the application"""
    activity_csv_files = list(Path(location).glob('*.csv'))
    if activity_csv_files:
        return activity_csv_files[0]
    else:
        raise FileNotFoundError('Activity CSV file not found!')


def parse_dividends(year=2018):
    def print_dividends():
        with open('dividends.csv', 'wt', newline='') as file_out:
            csv_out = csv.DictWriter(file_out, ['country', 'ticker', 'dividends_float', 'withholding_taxes_float'],
                                     extrasaction='ignore')
            csv_out.writeheader()
            csv_out.writerows(list(dividends_to_print.__dict__ for dividends_to_print in dividends_by_ticker.values()))

    csv_in = csv.DictReader(find_csv_file('../input/activity/').open(), fieldnames=[ActivityFieldIds.statement_type,
                                                                                    ActivityFieldIds.row_type])
    currency_rates = parse_currencies(year)
    finnish = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['fi'])
    finnish.install()
    dividends_by_ticker = {}
    for row in csv_in:
        statement_type = row.get(ActivityFieldIds.statement_type)
        if statement_type == 'Dividends' or statement_type == 'Withholding Tax':
            if row.get(ActivityFieldIds.row_type) == 'Header':
                csv_in.fieldnames += row.get(None)
            elif row.get(ActivityFieldIds.description):
                description = row.get(ActivityFieldIds.description).split('(')
                ticker = description[0].strip()
                country_code = description[1][:2]
                country_code = country_code if country_code.isalpha() else 'US'
                country = pycountry.countries.get(alpha_2=country_code).name
                country = _(country)
                timestamp = date.fromisoformat(row.get(ActivityFieldIds.date))
                if timestamp.year != year:
                    continue
                currency = row.get(ActivityFieldIds.currency)
                amount = Fraction(row.get(ActivityFieldIds.amount))
                while not currency_rates[currency].get(timestamp):
                    timestamp -= timedelta(days=1)
                amount_in_base_currency = amount / currency_rates[currency][timestamp]
                dividends = dividends_by_ticker.setdefault(ticker, Dividends(ticker, country))
                if statement_type == 'Dividends':
                    dividends.add_dividend(amount_in_base_currency)
                else:
                    dividends.add_withholding_tax(amount_in_base_currency)

    sum_of_dividends = Fraction()
    sum_of_withholding_taxes = Fraction()
    for dividends in dividends_by_ticker.values():
        if dividends.dividends > 0:
            sum_of_dividends += dividends.dividends
            sum_of_withholding_taxes += dividends.withholding_taxes
            print(dividends)
    print('\nTotal sum of dividends', round_fraction(sum_of_dividends), 'with paid taxes amounting to',
          round_fraction(sum_of_withholding_taxes))
    print_dividends()


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
