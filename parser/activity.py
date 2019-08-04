import csv
from collections import defaultdict
from fractions import Fraction
from pathlib import Path


class FieldIds:
    statement_type = '#st'
    row_type = '#rt'
    amount = 'Amount'
    description = 'Description'


def parse():
    def find_activity_csv_file():
        """Searches for and returns the first CSV file located in the "input/activity" folder of the application"""
        activity_csv_files = list(Path('../input/activity/').glob('*.csv'))
        if activity_csv_files:
            return activity_csv_files[0]
        else:
            raise FileNotFoundError('Activity CSV file not found!')
    csv_in = csv.DictReader(find_activity_csv_file().open(), fieldnames=[FieldIds.statement_type, FieldIds.row_type])
    dividends_by_ticker = defaultdict(Fraction)
    for row in csv_in:
        if row.get(FieldIds.statement_type) == 'Dividends':
            if row.get(FieldIds.row_type) == 'Header':
                csv_in.fieldnames += row.get(None)
            elif row.get(FieldIds.description):
                ticker = row.get(FieldIds.description).split('(')[0].strip()
                dividends_by_ticker[ticker] += Fraction(row.get(FieldIds.amount))
    for ticker, dividends in dividends_by_ticker.items():
        print(ticker, float(dividends))


parse()
