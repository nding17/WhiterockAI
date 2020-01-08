import csv
import numpy as np
import pandas as pd
import os
from os import listdir
from os.path import isfile, join

if __name__ == '__main__':

    data_path = '../data/Political_contributions'
    export_path = '../data/Political_contributions_CSV'

    years = [
        '2019',
        '2017-2018',
        '2015-2016',
        '2013-2014',
    ]

    columns = [[
        'election type',
        'entity',
        'donor',
        'city',
        'state',
        'zip code',
        'recipient',
        'recipient type',
        'date',
        'amount',
    ]]

    os.mkdir(export_path)

    for year in years:

        data_path_year = f'{data_path}/{year}'
        export_path_year = f'{export_path}/{year}'

        os.mkdir(export_path_year)

        filenames = [f.split('.')[0] for f in listdir(data_path_year) if isfile(join(data_path_year, f)) and 'dates' not in f]

        for fn in filenames:
            with open(f'{data_path_year}/{fn}.txt', 'r') as in_file:
                stripped = (line.strip() for line in in_file)
                lines = []

                for line in stripped:
                    if line:
                        line_data = line.split('|')
                        if len(line_data) == 20:
                            line = np.array(line_data)[np.r_[3,5:14]]
                        if len(line_data) == 21:
                            line = np.array(line_data)[np.r_[3,6:15]]
                        
                        lines.append(line)

                lines = tuple(lines)

                with open(f'{export_path_year}/{fn}.csv', 'w') as out_file:
                    writer = csv.writer(out_file)
                    writer.writerows(columns)
                    writer.writerows(lines)

            pd.read_csv(f'{export_path_year}/{fn}')\
              .drop_duplicates()\
              .reset_index()\
              .query('amount>0')\
              .to_csv(f'{export_path_year}/{fn}')
