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
    
    instructions = {
        'CHI_PLUTO_CLEANING': CHI_PLUTO_CLEANING,
        'CHI_SALES_CLEANING': CHI_SALES_CLEANING,
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

        return newdata_cl

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

        pluto_cl = pluto.copy().sort_values(by='SALE DATE') \
                               .drop_duplicates(subset=['PIN', 
                                                        'ADDRESS', 
                                                        'BLDG CODE', 
                                                        'LAND SF'], 
                                                keep='last') \
                               .reset_index(drop=True)

        return pluto_cl

if __name__ == '__main__':
    cp = cleaning_pipeline()
    ci = cleaning_instructions()
    ins = ci.instructions['CHI_PLUTO_CLEANING']
    api_id = cp._chi_pluto_api_id
    newdata = cp.pipeline_data(api_id, ins)

    ins_s = ci.instructions['CHI_SALES_CLEANING']
    api_id_s = cp._chi_sales_api_id
    newdata_s = cp.pipeline_data(api_id_s, ins_s)

    pluto_old = cp._load_old_pluto('../../data/CHI Data')
    cp._update_pluto_with_df(newdata, newdata_s)
