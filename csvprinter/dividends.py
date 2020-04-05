import csv
from collections import namedtuple

from csvprinter import get_csv_file


def print_to_csv(dividends_by_ticker):
    CountryDividends = namedtuple('CountryDividends', ['country', 'dividends', 'withholding_taxes'])
    countries = set(dividends.country for dividends in dividends_by_ticker.values())
    country_dividends_list = []
    for country in countries:
        sum_of_dividends_by_country = sum(
            ticker_dividends.dividends for ticker_dividends in dividends_by_ticker.values() if
            ticker_dividends.country == country)
        sum_of_withholding_taxes_by_country = sum(
            ticker_dividends.withholding_taxes for ticker_dividends in dividends_by_ticker.values() if
            ticker_dividends.country == country)
        country_dividends_list.append(
            CountryDividends(country, sum_of_dividends_by_country, sum_of_withholding_taxes_by_country))

    file = get_csv_file('dividends_by_country.csv')
    with open(file, 'w+', newline='') as file_out:
        csv_out = csv.DictWriter(file_out, ['country', 'dividends', 'withholding_taxes'],
                                 extrasaction='ignore')
        csv_out.writeheader()
        csv_out.writerows(list(country_dividends._asdict() for country_dividends in country_dividends_list))
    print('Dividends per country printed to', file)
    file = get_csv_file('dividends_by_stock.csv')
    with open(file, 'w+', newline='') as file_out:
        csv_out = csv.DictWriter(file_out, ['country', 'ticker', 'name', 'dividends', 'withholding_taxes'],
                                 extrasaction='ignore')
        csv_out.writeheader()
        csv_out.writerows(list(ticker_dividends.__dict__ for ticker_dividends in dividends_by_ticker.values() if
                               ticker_dividends.dividends > 0))
    print('Dividends per stock printed to', file)
