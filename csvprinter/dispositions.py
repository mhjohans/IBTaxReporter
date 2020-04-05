import csv

from csvprinter import get_csv_file


def print_to_csv(dispositions_by_ticker):
    file = get_csv_file('dispositions.csv')
    with open(file, 'w+', newline='') as file_out:
        csv_out = csv.DictWriter(file_out, ['ticker', 'name', 'amount', 'profits', 'losses'],
                                 extrasaction='ignore')
        csv_out.writeheader()
        csv_out.writerows(
            list(dispositions.__dict__ for dispositions in dispositions_by_ticker.values()))
    print('Dispositions printed to', file)
