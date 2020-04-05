import csv

from csvprinter import get_csv_file


def print_to_csv(dividends_by_ticker):
    file = get_csv_file('dividends.csv')
    with open(file, 'w+', newline='') as file_out:
        csv_out = csv.DictWriter(file_out, ['country', 'ticker', 'name', 'dividends', 'withholding_taxes'],
                                 extrasaction='ignore')
        csv_out.writeheader()
        csv_out.writerows(list(dividends_to_print.__dict__ for dividends_to_print in dividends_by_ticker.values() if
                               dividends_to_print.dividends > 0))
    print('Dividends printed to', file)
