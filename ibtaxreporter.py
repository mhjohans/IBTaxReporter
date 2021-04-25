from datetime import date

from csvparser.dispositions import parse_from_csv as parse_dispositions
from csvparser.dividends import parse_from_csv as parse_dividends
from csvprinter.dispositions import print_to_csv as print_dispositions
from csvprinter.dividends import print_to_csv as print_dividends

tax_year = date.today().year - 1
print('Starting reporting for tax year', tax_year)
print('Processing dividends...\n')
print_dividends(parse_dividends(tax_year))
print('\nProcessing dispositions...\n')
print_dispositions(parse_dispositions(tax_year))
