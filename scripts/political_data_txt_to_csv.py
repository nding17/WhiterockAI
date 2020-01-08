import csv
import numpy as np
import pandas as pd
import os
from os import listdir
from os.path import isfile, join

if __name__ == '__main__':

    data_path = '../data/Political_contributions'
    export_path = '../data/Political_contributions_CSV'

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

    os.makedirs(export_path, exist_ok=True)

    years = [y for y in listdir(data_path) if '.DS_Store' not in y]

    for year in years:

        data_path_year = f'{data_path}/{year}'
        export_path_year = f'{export_path}/{year}'

        os.makedirs(export_path_year, exist_ok=True)

        filenames = [f.split('.')[0] for f in listdir(data_path_year) if isfile(join(data_path_year, f)) and 'dates' not in f]

        for fn in filenames:
            with open(f'{data_path_year}/{fn}.txt', 'rb') as in_file:
                stripped = (line.strip() for line in in_file)
                lines = []

                for line in stripped:
                    if line:
                        line_data = str(line).split('|')
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

            pd.read_csv(f'{export_path_year}/{fn}.csv', index_col=0)\
              .drop_duplicates()\
              .query('amount>0')\
              .reset_index()\
              .to_csv(f'{export_path_year}/{fn}.csv', index=False)
