from csvparser.dispositions import parse_from_csv as parse_dispositions
from csvparser.dividends import parse_from_csv as parse_dividends
from csvprinter.dispositions import print_to_csv as print_dispositions
from csvprinter.dividends import print_to_csv as print_dividends

year = 2019
print('Starting reporting for tax year', year)
print('Processing dividends...\n')
print_dividends(parse_dividends(year))
print('\nProcessing dispositions...\n')
print_dispositions(parse_dispositions(year))
