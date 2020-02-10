import pandas as pd
import numpy as np
import os
from os import listdir
from os.path import isfile, join


if __name__ == '__main__':

    def gen_data_path(year, data_path):
        return f'{data_path}/{year}'

    def concat_dfs(data_path_year):
        filenames = [f for f in listdir(data_path_year) if isfile(join(data_path_year, f))]
        frames = []
        for fn in filenames:
            data = pd.read_csv(f'{data_path_year}/{fn}', error_bad_lines=False)
            frames.append(data)
        data_all = pd.concat(frames, ignore_index=True).reset_index(drop=True)
        
        return data_all

    def clean_zipcode(df):
        drop_indices = []
        for index, zipcode in enumerate(df['zip code']):
            zipcode = str(zipcode)

            if not zipcode.isdigit():
                drop_indices.append(index)
            
            if len(zipcode)<5:
                drop_indices.append(index)
        
        df_cleaned = df.drop(drop_indices)\
                       .reset_index(drop=True)
        
        df_cleaned['zip code'] = df_cleaned['zip code'].astype(str)\
                                                       .apply(lambda x: x[:5])

        return df_cleaned

    def gen_summary(df_cleaned, year):
        data_grouped = df_cleaned.groupby(['zip code']).agg({
            'amount': ['sum', 'mean', 'median', 'count']
        })

        data_grouped.columns = [f'total donations {year}', 
                                f'average donations {year}', 
                                f'median donations {year}', 
                                f'number of donations {year}']

        data_grouped = data_grouped.reset_index()
        
        data_final = pd.merge(data_grouped, 
                              df_cleaned[['zip code', 'state']].drop_duplicates(subset='zip code'), 
                              on='zip code', 
                              how='left')
        
        return data_final

    def summary_pipeline(year, data_path):
    
        data_path_year = gen_data_path(year, data_path)
        data_year = concat_dfs(data_path_year)
        data_year_cleaned = clean_zipcode(data_year)
        data_summary = gen_summary(data_year_cleaned, year)
        
        return data_summary

    pluto = pd.read_csv('../data/project/All_Properties PLUTO_New_Data.csv', index_col=0)
    pluto.ZIP = pluto.ZIP.astype(str)

    data_path = '../data/Political_contributions_CSV'
    years = [y for y in listdir(data_path) if '.DS_Store' not in y]

    for year in years:
        df_sum = summary_pipeline(year, data_path)
        df_sum.to_csv(f'../data/donations_summary/summary_{year}.csv', index=False)
        df_sum.rename(columns={'zip code': 'ZIP'}, inplace=True)
        
        pluto = pd.merge(pluto, 
                         df_sum[df_sum.columns[:-1]].drop_duplicates(subset='ZIP'),
                         on='ZIP',
                         how='left')

    pluto.to_csv('../data/project/All_Properties with Political_contributions PLUTO_New_Data.csv', index=False)
