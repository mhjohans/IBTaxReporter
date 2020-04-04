from csvparser.activity import parse_dividends
from printer.dividends import print_to_csv as print_dividends

year = 2019
print('Starting reporting for tax year', year)
print('Processing dividends...\n')
print_dividends(parse_dividends(year))
print('Dividends processed and printed.')
