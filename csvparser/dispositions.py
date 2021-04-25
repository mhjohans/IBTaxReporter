import csv
import decimal
from datetime import date, timedelta
from decimal import Decimal

import csvparser.currency as currency_parser
from csvparser import scrape_stock_name, find_csv_file, get_input_folder


class DispositionFieldIds:
    statement_type = '#st'
    row_type = '#rt'
    asset = 'Asset Category'
    datetime = 'Date/Time'
    currency = 'Currency'
    ticker = 'Symbol'
    amount = 'Proceeds'
    profit = 'Realized P/L'


class Dispositions:

    def __init__(self, ticker):
        self.name = scrape_stock_name(ticker)
        self.ticker = ticker
        self.amount = Decimal()
        self.profits = Decimal()
        self.losses = Decimal()

    def __str__(self):
        return '{}, {}, {}, {}'.format(self.ticker, self.name, self.amount, self.profits, self.losses)

    def add_disposition(self, amount, profit):
        self.amount += amount
        self.amount = round(self.amount, 2)
        if profit >= 0:
            self.profits += profit
            self.profits = round(self.profits, 2)
        else:
            self.losses += profit
            self.losses = round(self.losses, 2)


def parse_from_csv(year):
    csv_in = csv.DictReader(find_csv_file(get_input_folder('activity')).open(),
                            fieldnames=[DispositionFieldIds.statement_type,
                                        DispositionFieldIds.row_type])
    currency_rates = currency_parser.parse_currencies(year, currency_parser.CurrencyTimeFrame.DAILY)
    dispositions_by_ticker = {}
    decimal.getcontext().prec = 9
    header_read = False
    for row in csv_in:
        statement_type = row.get(DispositionFieldIds.statement_type)
        if statement_type == 'Trades':
            if row.get(DispositionFieldIds.row_type) == 'Header' and not header_read:
                csv_in.fieldnames += row.get(None)
                header_read = True
            elif row.get(DispositionFieldIds.row_type) == 'Data' and 'Forex' not in row.get(DispositionFieldIds.asset):
                profit = Decimal(row.get(DispositionFieldIds.profit))
                if profit != 0:
                    timestamp = date.fromisoformat(row.get(DispositionFieldIds.datetime).split(',')[0])
                    currency = row.get(DispositionFieldIds.currency)
                    if timestamp.year != year:
                        continue
                    while not currency_rates[currency].get(timestamp):
                        timestamp -= timedelta(days=1)
                    amount = Decimal(row.get(DispositionFieldIds.amount))
                    if amount < 0:
                        amount = amount.copy_abs()
                    amount_in_base_currency = amount / currency_rates[currency][timestamp]
                    profit_in_base_currency = profit / currency_rates[currency][timestamp]
                    ticker = row.get(DispositionFieldIds.ticker)
                    if ticker in dispositions_by_ticker:
                        dispositions = dispositions_by_ticker[ticker]
                    else:
                        dispositions = Dispositions(ticker)
                        dispositions_by_ticker[ticker] = dispositions
                    dispositions.add_disposition(amount_in_base_currency, profit_in_base_currency)

    sum_of_amounts = Decimal()
    sum_of_profits = Decimal()
    for dispositions in dispositions_by_ticker.values():
        sum_of_amounts += dispositions.amount
        sum_of_profits += dispositions.profits + dispositions.losses
        print(dispositions)
    print('\nTotal sum of dispositions', sum_of_amounts, '€ with profits amounting to',
          sum_of_profits, '€')
    return dispositions_by_ticker
