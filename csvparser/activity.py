import csv
import decimal
import gettext
from datetime import date, timedelta
from decimal import Decimal

import pycountry
import requests
from bs4 import BeautifulSoup

import csvparser
import csvparser.currency as currencyparser


class ActivityFieldIds:
    statement_type = '#st'
    row_type = '#rt'
    amount = 'Amount'
    description = 'Description'
    date = 'Date'
    currency = 'Currency'


class Dividends:

    def __init__(self, ticker, country):
        def scrape_stock_name():
            result = requests.get('https://finance.yahoo.com/quote/' + ticker)
            if result.ok:
                page_content = result.text
                soup = BeautifulSoup(page_content, features='lxml')
                name_tag = soup.find('h1')
                if name_tag:
                    ticker_and_name = name_tag.text
                    ticker_divider_index = ticker_and_name.find('-')
                    if ticker_divider_index != -1:
                        return ticker_and_name[ticker_divider_index + 2:]
            return ticker

        self.name = scrape_stock_name()
        self.ticker = ticker
        self.country = country
        self.dividends = Decimal()
        self.withholding_taxes = Decimal()

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.country, self.name, self.dividends, self.withholding_taxes)

    def add_dividend(self, dividend):
        self.dividends += dividend
        self.dividends = round(self.dividends, 2)

    def add_withholding_tax(self, withholding_tax):
        self.withholding_taxes += -withholding_tax
        self.withholding_taxes = round(self.withholding_taxes, 2)


def parse_dividends(year=2019):
    csv_in = csv.DictReader(csvparser.find_csv_file(csvparser.get_input_folder('activity')).open(),
                            fieldnames=[ActivityFieldIds.statement_type,
                                        ActivityFieldIds.row_type])
    currency_rates = currencyparser.parse_currencies(year)
    finnish = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['fi'])
    finnish.install()
    dividends_by_ticker = {}
    decimal.getcontext().prec = 9
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
                amount = Decimal(row.get(ActivityFieldIds.amount))
                while not currency_rates[currency].get(timestamp):
                    timestamp -= timedelta(days=1)
                amount_in_base_currency = amount / currency_rates[currency][timestamp]
                if ticker in dividends_by_ticker:
                    dividends = dividends_by_ticker[ticker]
                else:
                    dividends = Dividends(ticker, country)
                    dividends_by_ticker[ticker] = dividends
                if statement_type == 'Dividends':
                    dividends.add_dividend(amount_in_base_currency)
                else:
                    dividends.add_withholding_tax(amount_in_base_currency)

    sum_of_dividends = Decimal()
    sum_of_withholding_taxes = Decimal()
    for dividends in dividends_by_ticker.values():
        if dividends.dividends > 0:
            sum_of_dividends += dividends.dividends
            sum_of_withholding_taxes += dividends.withholding_taxes
            print(dividends)
    print('\nTotal sum of dividends', sum_of_dividends, '€ with paid taxes amounting to',
          sum_of_withholding_taxes, '€')
    return dividends_by_ticker
