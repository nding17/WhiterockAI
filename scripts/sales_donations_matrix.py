import pandas as pd
from datetime import datetime
from datetime import date
from os import listdir
from os.path import isfile, join
from functools import reduce
import numpy as np

if __name__ == '__main__':

	def merge_dfs(export_path, on, key):
	    filenames = [f for f in listdir(export_path) if isfile(join(export_path, f)) and f != '.DS_Store']
	    dfs = []
	    
	    for fn in filenames:
	        df = pd.read_csv(f'{export_path}/{fn}')
	        dfs.append(df)
	    
	    df_merged = reduce(lambda left,right: pd.merge(left,right,on=[on],
	                                            how='outer'), dfs)
	    
	    columns = df_merged.columns
	    accepted = [col for col in columns if key in col]
	    
	    return df_merged[[on]+accepted]

	def gen_submarket_dict(pluto_path):
		pluto = pd.read_csv(pluto_path)
		dict_submarket = dict(zip(pluto['ZIP'].astype(str), pluto['REIS SUBMARKET']))
		return dict_submarket

	def assign_submarket(zipcode, dict_submarket):
	    try:
	        return dict_submarket[zipcode]
	    except:
	        return None

	def export_matrix(export_path, sales, donations, dict_submarket):
		sales_zipcodes = sales_summary['ZIP'].unique()
		donations_zipcodes = donations_summary['ZIP'].unique()
		zipcodes = list(set(sales_zipcodes).intersection(set(donations_zipcodes)))

		sales_data = sales_summary.loc[sales_summary.ZIP.isin(zipcodes)][sales_summary.columns]\
								  .reset_index(drop=True)
		donations_data = donations_summary.loc[donations_summary.ZIP.isin(zipcodes)][donations_summary.columns]\
										  .reset_index(drop=True)

		full_data = pd.merge(sales_data, donations_data, on='ZIP', how='outer').astype(dtype={'ZIP': str})
		full_data['submarket'] = full_data['ZIP'].apply(lambda x: assign_submarket(x, dict_submarket))

		submarkets = [sub for sub in full_data.submarket.unique() if sub is not None]

		for submarket in submarkets:
			df_sub = full_data[full_data.submarket==submarket]
			df_corr = df_sub.corr()
			filename = submarket.replace(' ', '_')\
								.replace('/', '_')
			df_corr.to_csv(f'{export_path}/{filename}_corr_matrix.csv')

	sales_dir_path = '../data/project/sales_summary'
	donations_dir_path = '../data/project/Political_contributions_summary'
	pluto_data_path = '../data/project/All_Properties with Political_contributions PLUTO_New_Data.csv'
	matrix_dir_path = '../data/project/Sales_donations_matrices'

	sales_summary = merge_dfs(sales_dir_path, 'ZIP', 'average')
	donations_summary = merge_dfs(donations_dir_path, 'zip code', 'total').rename(columns={'zip code': 'ZIP'})
	dict_submarket = gen_submarket_dict(pluto_data_path)

	export_matrix(matrix_dir_path, 
				  sales_summary, 
				  donations_summary, 
				  dict_submarket)
