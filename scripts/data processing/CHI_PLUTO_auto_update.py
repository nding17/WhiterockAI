### package requirements
import pandas as pd
import numpy as np
import warnings
import urllib
import os
import time
import requests

from datetime import datetime
from datetime import date
from urllib.request import urlopen
from lycleaner import Address_cleaner
from sodapy import Socrata

class cleaning_instructions:

    CHI_PLUTO_CLEANING = {
        'pin': {
            'delete': 0,
            'new name': 'PIN',
        },
        'class': {
            'delete': 0,
            'new name': 'BLDG CODE',
        },
        'tax_year': {
            'delete': 0,
            'new name': 'TAX YEAR',
        },
        'nbhd': {
            'delete': 0,
            'new name': 'NEIGHBORHOOD',
        },
        'hd_sf': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'town_code': {
            'delete': 0,
            'new name': 'TOWN',
        },
        'type_resd': {
            'delete': 0,
            'new name': 'BLDG CAT',
        },
        'apts': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'ext_wall': {
            'delete': 0,
            'new name': 'EXT MATERIAL',
        },
        'roof_cnst': {
            'delete': 0,
            'new name': 'ROOF MATERIAL',
        },
        'rooms': {
            'delete': 0,
            'new name': '# ROOMS',
        },
        'beds': {
            'delete': 0,
            'new name': '# BED',
        },
        'bsmt': {
            'delete': 0,
            'new name': 'BASEMENT',
        },
        'bsmt_fin': {
            'delete': 0,
            'new name': 'BASEMENT COND',
        },
        'heat': {
            'delete': 0,
            'new name': 'CENTRAL HEATING',
        },
        'oheat': {
            'delete': 0,
            'new name': 'OTHER HEATING',
        },
        'air': {
            'delete': 0,
            'new name': 'CENTRAL AIR',
        },
        'frpl': {
            'delete': 0,
            'new name': '# FIREPLACE',
        },
        'attic_type': {
            'delete': 0,
            'new name': 'ATTIC',
        },
        'attic_fnsh': {
            'delete': 0,
            'new name': 'ATTIC COND',
        },
        'hbath': {
            'delete': 0,
            'new name': '# POWDER',
        },
        'tp_plan': {
            'delete': 1,
        },
        'tp_dsgn': {  
            'delete': 0,
            'new name': 'CATHEDRAL CEILING',
        },
        'cnst_qlty': {
            'delete': 0,
            'new name': 'CONST QUALITY',
        },
        'renovation': {
            'delete': 1,
        },
        'site': {
            'delete': 1,
        },
        'gar1_size': {
            'delete': 0,
            'new name': 'GARAGE 1',
        },
        'gar1_cnst': {
            'delete': 0,
            'new name': 'GARAGE 1 MATERIAL',
        },
        'gar1_att': {
            'delete': 0,
            'new name': 'GARAGE ATTACHED',
        },
        'gar1_area': {
            'delete': 0,
            'new name': 'GARAGE 1 AREA'
        },
        'gar2_size': {
            'delete': 1,
        },
        'gar2_cnst': {
            'delete': 1,
        },
        'gar2_att': {
            'delete': 1,
        },
        'gar2_area': {
            'delete': 1,
        },
        'porch': {
            'delete': 0,
            'new name': 'ENCLOSED PORCH',
        },
        'ot_impr': {
            'delete': 1,
        },
        'bldg_sf': {
            'delete': 0,
            'new name': 'GSF',
        },
        'repair_cnd': {
            'delete': 0,
            'new name': 'INT COND',
        },
        'multi_code': {
            'delete': 0,
            'new name': '# BLDG',
        },
        'ncu': {
            'delete': 0,
            'new name': '# COMM',
        },
        'pri_est_land': {
            'delete': 0,
            'new name': 'LAND ASSD $ PY',
        },
        'pri_est_bldg': {
            'delete': 0,
            'new name': 'BLDG ASSD $ PY',
        },
        'most_recent_sale_date': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
        'doc_no': {
            'delete': 0,
            'new name': 'Deed No.',
        },
        'most_recent_sale_price': {
            'delete': 0,
            'new name': 'SALE PRICE',
        },
        'centroid_x': {
            'delete': 0,
            'new name': 'LONGITUDE',
        },
        'centroid_y': {
            'delete': 0,
            'new name': 'LATITUDE',
        },
        'tractce': {
            'delete': 1,
        },
        'total_bldg_sf': {
            'delete': 0,
            'new name': 'Total Building Square Feet',
        },
        'multi_ind': {
            'delete': 1,
        },
        'addr': {
            'delete': 0,
            'new name': 'ADDRESS',
        },
        'modeling_group': {
            'delete': 0,
            'new name': 'Modeling Group',
        },
        'fbath': {
            'delete': 0,
            'new name': '# BATH',
        },
        'age': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'use_1': {
            'delete': 0,
            'new name': 'PROPERTY TYPE',
        },
        'n_units': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'per_ass': {
            'delete': 1,
        },
        'condo_class_factor': {
            'delete': 1,
        },
        'multi_family_ind': {
            'delete': 1,
        },
        'large_lot': {
            'delete': 1,
        },
        'deed_type': {
            'delete': 1,
        },
        'o_hare_noise': {
            'delete': 0,
            'new name': 'AIRPORT NOISE',
        },
        'floodplain': {
            'delete': 0,
            'new name': 'FEMA',
        },
        'near_major_road': {
            'delete': 0,
            'new name': 'Near Major Road',
        },
        'total_units': {
            'delete': 1,
        },
        'condo_strata': {
            'delete': 1,
        },
        'age_squared': {
            'delete': 1,
        },
        'age_decade': {
            'delete': 1,
        },
        'age_decade_squared': {
            'delete': 1,
        },
        'lot_size_squared': {
            'delete': 1,
        },
        'improvement_size_squared': {
            'delete': 1,
        },
        'location_factor': {
            'delete': 1,
        },
        'garage_indicator': {
            'delete': 1,
        },
        'residential_share_of_building': {
            'delete': 1,
        },
        'pure_market_sale': {
            'delete': 1,
        },
        'pure_market_filter': {
            'delete': 1,
        },
        'neigborhood_code_mapping_': {
            'delete': 1,
        },
        'square_root_of_lot_size': {
            'delete': 1
        },
        'square_root_of_age': {
            'delete': 1,
        },
        'square_root_of_improvement_size': {
            'delete': 1
        },
        'town_and_neighborhood': {
            'delete': 0,
            'new name': 'Town and Neighborhood'
        }
    }

    CHI_SALES_CLEANING_ADD = {
        'sale_date': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
        'sale_year': {
            'delete': 1,
        },
        'sale_quarter': {
            'delete': 1,
        },
        'sale_half_year': {
            'delete': 1,
        },
        'sale_quarter_of_year': {
            'delete': 1,
        },
        'sale_month_of_year': {
            'delete': 1,
        },
        'sale_half_of_year': {
            'delete': 1,
        },
        'town_and_neighborhood_sf_group_only': {
            'delete': 0,
            'new name': 'Town and Neighborhood, SF Group Only'
        },
        'most_recent_sale': {
            'delete': 0,
            'new name': 'Most Rencent Sale'
        },
        'road_proximity': {
            'delete': 0,
            'new name': 'Road Proximity'
        },
        'est_bldg': {
            'delete': 0,
            'new name': 'Estimate (Building)',
        },
        'est_land': {
            'delete': 0,
            'new name': 'Estimate (Land)',
        },
        'sale_price': {
            'delete': 0,
            'new name': 'SALE PRICE',
        }
    }

    # combine two different dictionaries 
    CHI_SALES_CLEANING = {**CHI_PLUTO_CLEANING, **CHI_SALES_CLEANING_ADD}

    REIS_RENAME = {
        'Property Type': 'PROPERTY TYPE',
        'Street Address': 'ADDRESS',
        'City': 'CITY',
        'State': 'STATE',
        'Zip': 'ZIP',
        'County': 'COUNTY',
        'Year Renovated': 'YEAR RENOVATED',
        'Asking Rent (Units)': 'ASKING RENT (UNITS)',
        'Asking Rent (SF)': 'ASKING RENT (SF)',
        'Vacancy': 'VACANCY',
        'Building Class': 'BLDG CLASS',
        'Cap Rate': 'CAP RATE',
        'Sale Price': 'SALE PRICE',
        'Sale Date': 'SALE DATE',
        'Transaction Type': 'TRANSACTION TYPE',
        'Buyer': 'BUYER',
        'Year Built': 'YEAR BUILT',
        'Seller': 'SELLER',
        'Construction Status': 'CONSTRUCTION STATUS',
        'Expected Completion': 'EXPECTED COMPLETION',
        'Expected Groundbreak': 'EXPECTED GROUNDBREAK',
        'Developer': 'DEVELOPER',
        'Developer Phone': 'DEVELOPER PHONE',
        'Sector Name': 'SECTOR NAME',
        'Submarket': 'REIS SUBMARKET',
    }

    CHI_COL_MAPPING = {
        'GARAGE ATTACHED': {
            '2': '0',
        },
        'GARAGE 1 AREA': {
            '2': '0',
        },  
        'GARAGE 1': {
            '1': '1',
            '2': '1.5',
            '3': '2',
            '4': '2.5',
            '5': '3',
            '6': '3.5',
            '7': '0',
            '8': '4',
            '9': '4.5',
            '10': '5',
            '11': '5.5',
            '12': '6',
        },
        'BLDG CODE': {
            '202': 'SMALL 1 STORY',
            '203': 'MEDIUM 1 STORY',
            '204': 'LARGE 1 STORY',
            '210': 'TOWNHOUSE',
            '211': 'MULTI: 2 TO 6 UNITS',
            '212': 'MIXED USE',
            '234': 'SPLIT LEVEL',
            '295': 'TOWNHOUSE',
            '205': '2 OR MORE STORIES',
            '206': '2 OR MORE STORIES',
            '207': '2 OR MORE STORIES',
            '208': '2 OR MORE STORIES',
            '209': '2 OR MORE STORIES',
            '278': '2 OR MORE STORIES',
        },
        'BLDG CAT': {
            '1': '1',
            '2': '2',
            '3': '3',
            '5': '1.5',
            '6': '1.5',
            '7': '1.5',
            '8': '1.5',
            '9': '1.5',
        }
    }
    
    instructions = {
        'CHI_PLUTO_CLEANING': CHI_PLUTO_CLEANING,
        'CHI_SALES_CLEANING': CHI_SALES_CLEANING,
        'REIS_RENAME': REIS_RENAME,
        'CHI_COL_MAPPING': CHI_COL_MAPPING,
    }

class cleaning_pipeline:

    def __init__(self):
        self._chi_pluto_api_id = 'bcnq-qi2z'
        self._chi_sales_api_id = '5pge-nu6u'

    ### extract data from API 
    def _extract_data(self, api_id):
        # MAX_LIMIT = 1000000000
        MAX_LIMIT = 10000
        client = Socrata("datacatalog.cookcountyil.gov", None)
        results = client.get(api_id, limit=MAX_LIMIT)
        data = pd.DataFrame.from_records(results)
        return data

    ### standardizing the column names of the dataframes 
    def _clean_data(self, data, ins):
        orig_cols = [*ins.keys()] # original column names to be updated
        valid_cols = list(set(orig_cols).intersection(set(data.columns)))
        newdata = data.copy()[valid_cols] # sales data cleaned 
            
        for column in valid_cols:
            if ins[column]['delete'] == 1:
                newdata = newdata.drop([column], axis=1)
            if ins[column]['delete'] == 0:
                newdata = newdata.rename(columns={column: ins[column]['new name']})

        newdata_cl = newdata.copy().drop_duplicates(subset=['PIN', 'ADDRESS', 'BLDG CODE', 'LAND SF'])
        newdata_cl = newdata_cl.astype({
                        'PIN': str, 
                        'ADDRESS': str,
                        'BLDG CODE': str,
                        'LAND SF': str}, 
                    errors='ignore').reset_index(drop=True)

        newdata_cl['SALE DATE'] = pd.to_datetime(newdata_cl['SALE DATE'])

        cleaner = Address_cleaner()
        newdata_cl['ADDRESS'] = cleaner.easy_clean(newdata_cl['ADDRESS'].str.upper())

        newdata_cl = newdata_cl.loc[:,~newdata_cl.columns.duplicated()]
        newdata_final = newdata_cl.copy().reindex(columns=newdata_cl.columns.tolist()+['BLDG CODE DEF', '# FLOORS'])  

        return newdata_final

    def _update_pluto_with_df(self, pluto_old, df_new, cols_id=['PIN', 'ADDRESS', 'BLDG CODE', 'LAND SF']):
        # make sure there are no duplicated columns 
        # to prevent conflicts 
        pluto_old = pluto_old.loc[:,~pluto_old.columns.duplicated()]
        df_new = df_new.loc[:,~df_new.columns.duplicated()]

        # all the columns of the old PLUTO
        cols_op = pluto_old.columns.tolist()
        # all the columns of the new PLUTO
        cols_np = df_new.columns.tolist()

        # PLUTO update dataframe
        # added emtpy columns to be added later on
        added_cols = list(set(cols_np)-set(cols_op))
        pluto_up = pluto_old.copy().reindex(columns=cols_op+added_cols)


        pluto_up_check = pluto_up.drop_duplicates(subset=cols_id).reset_index(drop=True) # reset index
        df_new_check = df_new.drop_duplicates(subset=cols_id).reset_index(drop=True) # make sure the index is not messed up

        # ADDRESS, BLOCK, LOT and # UNITS combined are unique identifiers of the 
        # properties in PLUTO
        id_up = pluto_up_check[cols_id] # identifiers for the old PLUTO
        id_new = df_new_check[cols_id] # identifiers for the new PLUTO

        # find the same identifiers: identifiers that exist in both new and old PLUTO data
        # as well as the different identifiers that are unique in each PLUTO data
        same_id = pd.merge(id_up, id_new, on=cols_id, how='inner')
        diff_id = id_new.loc[~id_new.set_index(cols_id).index.isin(same_id.set_index(cols_id).index)] # diff identifiers

        print(f'{id_new.shape[0]} rows to be integrated in total')
        print(f'{same_id.shape[0]} rows to be updated, {diff_id.shape[0]} rows to be added')

        if same_id.shape[0]>0:
            df_new = df_new.reset_index(drop=True)
            pluto_up = pluto_up.reset_index(drop=True)

            # the index of a list of the same identifiers in the new PLUTO
            idx_sid_new = df_new.loc[df_new.set_index(cols_id).index.isin(same_id.set_index(cols_id).index)].index.tolist()
            # the index of a list of the same identifiers in the old PLUTO
            idx_sid_up = pluto_up.loc[pluto_up.set_index(cols_id).index.isin(same_id.set_index(cols_id).index)].index.tolist()

            # update the old PLUTO with the data in the new PLUTO
            cols_update = list(set(cols_np)-set(cols_id))
            pluto_up.at[idx_sid_up, cols_update] = df_new[cols_update].iloc[idx_sid_new]

        # concat the updated PLUTO with new property data that's not 
        # already in the old PLUTO file
        pluto_up = pd.concat([pluto_up, df_new.loc[df_new.set_index(cols_id).index.isin(diff_id.set_index(cols_id).index)]], sort=False)

        return pluto_up

    ### data pipeline for extracting and cleaning new data 
    def pipeline_data(self, api_id, ins):
        data = self._extract_data(api_id)
        newdata = self._clean_data(data, ins)
        return newdata

    ### load the base PLUTO data file for update
    def _load_old_pluto(self, pluto_path):
        pluto = pd.read_csv(f'{pluto_path}/CHIPL-001 All_Properties PLUTO.csv', low_memory=False)
        pluto = pluto.dropna(subset=['PIN', 'ADDRESS'])
        pluto = pluto.drop_duplicates()

        pluto['PIN'] = pluto['PIN'].astype(str, errors='ignore') \
                                   .apply(lambda x: x.split('.')[0])

        pluto['LAND SF'] = pluto['LAND SF'].apply(lambda x: x.replace(',', ''))

        pluto['BLDG CODE'] = pluto['BLDG CODE'].astype(str, errors='ignore') \
                                               .apply(lambda x: x.split('.')[0])

        cleaner = Address_cleaner()
        pluto['ADDRESS'] = cleaner.easy_clean(pluto['ADDRESS'].str.upper())

        pluto['SALE DATE'] = pd.to_datetime(pluto['SALE DATE'])

        pluto_cl = pluto.copy().sort_values(by='SALE DATE') \
                               .drop_duplicates(subset=['PIN', 
                                                        'ADDRESS', 
                                                        'BLDG CODE', 
                                                        'LAND SF'], 
                                                keep='last') \
                               .reset_index(drop=True)

        return pluto_cl

    ### update the PLUTO with the most recent sales data cleaned and processed earlier 
    def _update_pluto_with_sales_data(self, pluto, sales, deltadays):
        delta = pd.Timedelta(deltadays)
        sales = sales.sort_values(by=['SALE DATE'], ascending=False)
        latest_date = sales['SALE DATE'].iloc[0]
        earliest_date = latest_date-delta
        keep_index = sales[(sales['SALE DATE']>=earliest_date) & 
                           (sales['SALE DATE']<=latest_date)].index.tolist()
        sales_sub = sales.iloc[keep_index].reset_index(drop=True)

        sales_sub = sales_sub.sort_values(by='SALE DATE') \
                             .drop_duplicates(subset=['PIN', 'ADDRESS', 'BLDG CODE', 'LAND SF'], 
                                              keep='last')

        final_pluto = self._update_pluto_with_df(pluto, sales_sub)

        return final_pluto

    def _load_reis(self, reis_path):
        reis = pd.read_excel(f'{reis_path}/REIS Full Property Report 150k.xlsx')
        return reis

    def _clean_reis(self, reis):
        cl = cleaning_instructions() # cleaning instructions for sales data
        ins = cl.instructions['REIS_RENAME']
        reis_cl = reis.rename(columns=ins, errors='raise')
        reis_cl = reis_cl[[*ins.values()]]

        cleaner = Address_cleaner()
        reis_cl['ADDRESS'] = reis_cl['ADDRESS'].astype(str)
        reis_cl['ADDRESS'] = cleaner.easy_clean(reis_cl['ADDRESS'].str.upper())

        reis_cl = reis_cl.reindex(reis_cl.columns.tolist(), axis=1) \
                         .astype(dtype={'SALE DATE': str})
        
        reis_cl['SALE DATE'] = pd.to_datetime(reis_cl['SALE DATE'])
        reis_cl = reis_cl.sort_values(by=['SALE DATE'], ascending=False) \
                         .reset_index(drop=True)

        return reis_cl

    def pipeline_reis_data(self, reis_path):
        reis = self._load_reis(reis_path)
        reis_cl = self._clean_reis(reis)
        return reis_cl

    def _process_pluto(self, pluto):

        pluto['Total Building Square Feet'] = pluto['Total Building Square Feet'].astype(float, errors='ignore')

        drop_index = pluto[pluto['Modeling Group']=='NCHARS'].index.tolist() + \
                     pluto[pluto['Total Building Square Feet']>0].index.tolist() + \
                     pluto[pluto['BLDG CODE']=='299'].index.tolist()

        pluto_final = pluto.copy().drop(drop_index).reset_index(drop=True)

        pluto_final = pluto_final.astype({
                'GARAGE ATTACHED': str,
                'GARAGE 1 AREA': str,
                'GARAGE 1': str,
                'BLDG CODE': str,
                'BLDG CAT': str,
            }, errors='ignore')

        pcols = ['GARAGE ATTACHED', 
                 'GARAGE 1 AREA', 
                 'GARAGE 1', 
                 'BLDG CODE', 
                 'BLDG CAT']

        for col in pcols:
            pluto_final[col] = pluto_final[col].apply(lambda x: str(x).split('.')[0] if float(x).is_integer() else str(x))

        ci = cleaning_instructions()
        ins = ci.instructions['CHI_COL_MAPPING']

        # map the values to the corresponding values in WHITEROCK 
        pluto_final['GARAGE ATTACHED'] = pluto_final['GARAGE ATTACHED'].map(ins['GARAGE ATTACHED'])
        pluto_final['GARAGE 1 AREA'] = pluto_final['GARAGE 1 AREA'].map(ins['GARAGE 1 AREA'])
        pluto_final['GARAGE 1'] = pluto_final['GARAGE 1'].map(ins['GARAGE 1'])
        pluto_final['BLDG CODE DEF'] = pluto_final['BLDG CODE'].map(ins['BLDG CODE'])
        pluto_final['# FLOORS'] = pluto_final['BLDG CAT'].map(ins['BLDG CAT'])

        pluto_final = pluto_final.reset_index(drop=True)

        # Process the YEAR BUILT: substract the current year from the year in the original df 
        pluto_final['YEAR BUILT'] = pluto_final['YEAR BUILT'].astype(float)

        # select the year that is not NaN and process it 
        idx = pluto_final[~pluto_final['YEAR BUILT'].isnull()].index
        pluto_final['YEAR BUILT'].iloc[idx] = pluto_final['YEAR BUILT'].iloc[idx].astype(int)

        # subtract the current year from the year in the original data
        current_year = int(date.today().year)
        pluto_final['YEAR BUILT'].iloc[idx] = current_year-pluto_final['YEAR BUILT'].iloc[idx]['YEAR BUILT']

        pluto_final = pluto_final.reset_index(drop=True)
        
        return pluto_final

    def _export_pluto(self, pluto_final, output_path):
        date_today = str(date.today())
        pluto_final.to_csv(f'{output_path}/CHIPL-001 All_Properties PLUTO {date_today}.csv')

    def pipeline(self, pluto_path, reis_path, ouput_path):
        ci = cleaning_instructions()
        ins = ci.instructions

        print('>>> Downloanding and cleaning sales data, takes a while')
        sales_data = self.pipeline_data(self._chi_sales_api_id, ins['CHI_SALES_CLEANING'])

        print('>>> Downloading and cleaning new PLUTO, takes a while, please be patient')
        pluto_new = self.pipeline_data(self._chi_pluto_api_id, ins['CHI_PLUTO_CLEANING'])

        print('>>> Loading and cleaning old PLUTO')
        pluto_old = self._load_old_pluto(pluto_path)

        print('>>> Updating old PLUTO with new PLUTO')
        pluto_stage1 = self._update_pluto_with_df(pluto_old, pluto_new)

        print('>>> Updating [stage 1] PLUTO with sales data')
        pluto_stage2 = self._update_pluto_with_sales_data(pluto_stage1, sales_data, 40)

        print('>>> Loading and cleaning REIS')
        reis = self.pipeline_reis_data(reis_path)

        print('>>> Updating [stage 2] PLUTO with REIS')
        pluto_stage3 = self._update_pluto_with_df(pluto_stage2, reis, cols_id=['ADDRESS'])

        print('>>> Processing [final stage] PLUTO')
        pluto_final = self._process_pluto(pluto_stage3)

        print('>>> Exporting final PLUTO')
        self._export_pluto(pluto_final, output_path)

        print('>>> Job Done! Congratulations!')


if __name__ == '__main__':
    pluto_path = '../../data/CHI Data'
    reis_path = '../../data/CHI Data'
    output_path = '../../data'

    cp = cleaning_pipeline()
    cp.pipeline(pluto_path, reis_path, output_path)
