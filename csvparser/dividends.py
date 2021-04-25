import csv
import decimal
import gettext
from datetime import date
from decimal import Decimal

import pycountry

import csvparser.currency as currency_parser
from csvparser import scrape_stock_name, find_csv_file, get_input_folder


class DividendFieldIds:
    statement_type = '#st'
    row_type = '#rt'
    date = 'Date'
    currency = 'Currency'
    description = 'Description'
    amount = 'Amount'


class Dividends:

    def __init__(self, ticker, country):
        self.name = scrape_stock_name(ticker)
        self.ticker = ticker
        self.country = country
        self.dividends = Decimal()
        self.withholding_taxes = Decimal()

    def __str__(self):
        return '{}, {}, {}, {}, {}'.format(self.country, self.ticker, self.name, self.dividends, self.withholding_taxes)

    def add_dividend(self, dividend):
        self.dividends += dividend
        self.dividends = round(self.dividends, 2)

    def add_withholding_tax(self, withholding_tax):
        self.withholding_taxes += -withholding_tax
        self.withholding_taxes = round(self.withholding_taxes, 2)


def parse_from_csv(year):
    csv_in = csv.DictReader(find_csv_file(get_input_folder('activity')).open(),
                            fieldnames=[DividendFieldIds.statement_type,
                                        DividendFieldIds.row_type])
    currency_rates = currency_parser.parse_currencies(year, currency_parser.CurrencyTimeFrame.ANNUAL)
    finnish = gettext.translation('iso3166', pycountry.LOCALES_DIR, languages=['fi'])
    finnish.install()
    dividends_by_ticker = {}
    decimal.getcontext().prec = 9
    for row in csv_in:
        statement_type = row.get(DividendFieldIds.statement_type)
        if statement_type == 'Dividends' or statement_type == 'Withholding Tax':
            if row.get(DividendFieldIds.row_type) == 'Header':
                csv_in.fieldnames += row.get(None)
            elif row.get(DividendFieldIds.description):
                description = row.get(DividendFieldIds.description).split('(')
                ticker = description[0].strip()
                country_code = description[1][:2]
                country_code = country_code if country_code.isalpha() else 'US'
                country = pycountry.countries.get(alpha_2=country_code).name
                country = _(country)
                currency = row.get(DividendFieldIds.currency)
                timestamp = date.fromisoformat(row.get(DividendFieldIds.date))
                if timestamp.year != year:
                    continue
                amount = Decimal(row.get(DividendFieldIds.amount))
                amount_in_base_currency = amount / currency_rates[currency]
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
    print('\nTotal sum of dividends', sum_of_dividends, '€ with paid withholding taxes amounting to',
          sum_of_withholding_taxes, '€')
    return dividends_by_ticker
