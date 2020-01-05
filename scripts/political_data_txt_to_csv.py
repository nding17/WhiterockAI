import csv
import os
from os import listdir
from os.path import isfile, join

if __name__ == '__main__':

    data_path = '../data/Political_contributions_2019'
    export_path = '../data/political_data_2019_csv'

    os.mkdir(export_path)

    filenames = [f.split('.')[0] for f in listdir(data_path) if isfile(join(data_path, f))]

    for fn in filenames:
        with open(f'{data_path}/{fn}.txt', 'r') as in_file:
            stripped = (line.strip() for line in in_file)
            lines = (line.split("|") for line in stripped if line)
            with open(f'{export_path}/{fn}.csv', 'w') as out_file:
                writer = csv.writer(out_file)
                writer.writerows(lines)