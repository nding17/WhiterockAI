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
from bs4 import BeautifulSoup
from zipfile import ZipFile
from io import BytesIO
from cleaning_instructions import ci

class phl_cleaning_pipeline:

    def __init__(self):
        pass

    ### delete redundant columns and rename some columns 
    ### to match the names of the PLUTO data
    def pre_clean_df(self, df, instructions):
        PHL_COLS_ADD = instructions['PHL_COLS_ADD']
        PHL_PLUTO_RENAME = instructions['PHL_PLUTO_RENAME']
        orig_columns = list(instructions['PHL_PLUTO_RENAME'].keys())
        df_new = df.copy()[orig_columns]
        
        for column in orig_columns:
            if PHL_PLUTO_RENAME[column]['delete'] == 1:
                df_new = df_new.drop([column], axis=1)
            if PHL_PLUTO_RENAME[column]['delete'] == 0:
                df_new = df_new.rename(columns={column: PHL_PLUTO_RENAME[column]['new name']})
        
        df_new = df_new.reindex(df_new.columns.tolist()+PHL_COLS_ADD, axis=1) \
                       .astype(dtype={'SALE DATE': str})
        
        df_new['SALE DATE'] = pd.to_datetime(df_new['SALE DATE'])
        df_new = df_new.sort_values(by=['SALE DATE'], ascending=False) \
                       .reset_index(drop=True)
        
        return df_new

    ### subset the most recent data from the downloaded data based on 
    ### the order of date
    def subset_df_date(self, df_new, deltadays):
        delta = pd.Timedelta(deltadays)
        df_new = df_new.sort_values(by=['SALE DATE'], ascending=False)
        latest_date = df_new['SALE DATE'].iloc[0]
        earliest_date = latest_date-delta
        keep_index = df_new[(df_new['SALE DATE']>=earliest_date) & 
                            (df_new['SALE DATE']<=latest_date)].index
        df_sub = df_new.iloc[keep_index] \
                       .reset_index(drop=True)

        # drop the properties that are not good for backtesting
        drop_index = df_sub[df_sub['BLDG CAT']=='Commercial'].index.tolist() + \
                     df_sub[df_sub['BLDG CAT']=='Industrial'].index.tolist() + \
                     df_sub[df_sub['BLDG CAT']=='Vacant Land'].index.tolist() + \
                     df_sub[df_sub['LAND SF']==0].index.tolist() + \
                     df_sub[df_sub['GSF']<800].index.tolist() + \
                     df_sub[df_sub['SALE PRICE']<25000].index.tolist()

        df_sub = df_sub.drop(drop_index) \
                       .reset_index(drop=True)

        return df_sub

    ### update the PLUTO data, replace pre-existed record and 
    ### fill in new downloaded data
    def update_PLUTO(self, pluto, df_sub):
        pluto['SALE DATE'] = pd.to_datetime(pluto['SALE DATE'])
        pluto = pluto.sort_values(by=['SALE DATE'], ascending=False)

        pluto_addresses = pluto['ADDRESS'].tolist()
        sub_addresses = df_sub['ADDRESS'].tolist()
        pluto_update = pluto.copy()
        df_added = pd.DataFrame(columns=pluto.columns)
        df_sub = df_sub[pluto.columns]

        ### loop through all the addresses in the new data 
        ### to match the addresses in the PLUTO dataset 
        for address in sub_addresses:
            if address in pluto_addresses:
                added = df_sub[df_sub['ADDRESS']==address]['PARCEL ID'] \
                            .values.tolist()
                original = pluto[pluto['ADDRESS']==address]['PARCEL ID'] \
                            .values.tolist()
                
                # address in the PLUTO whose data need to be updated 
                if set(added) == set(original):
                    pluto_update.at[
                        pluto_update[pluto_update['ADDRESS']==address].index,
                        ['GSF', 'SALE PRICE', 'SALE DATE']
                    ] = df_sub[df_sub['ADDRESS']==address][['GSF', 'SALE PRICE', 'SALE DATE']] \
                          .values\
                          .tolist()
                else:
                    commons = set(added).intersection(set(original))
                    diffs = set(added) - set(original)

                    for pid in list(commons):
                        pluto_update.at[
                            pluto_update[(pluto_update['ADDRESS']==address) & 
                                         (pluto_update['PARCEL ID']==pid)].index,
                            ['GSF', 'SALE PRICE', 'SALE DATE']
                        ] = df_sub[(df_sub['ADDRESS']==address) & 
                                   (df_sub['PARCEL ID']==pid)][['GSF', 'SALE PRICE', 'SALE DATE']] \
                                  .values\
                                  .tolist()

                    if not diffs:
                        # to account for the addresses that have multiple properties
                        added_rows = df_sub.loc[(df_sub['ADDRESS']==address) &
                                                (df_sub['PARCEL ID'].isin(list(diffs)))]
                        for i in range(added_rows.shape[0]):
                            df_added = df_added.append(added_rows.iloc[i], 
                                                       ignore_index=True)

                        new_addrs = added_rows['ADDRESS'].values
                        if new_addrs:
                            print(f'\tadded address: {new_addrs[0]}')
            else:
                added_row = df_sub[df_sub['ADDRESS']==address]
                df_added = df_added.append(added_row, ignore_index=True)

                new_addrs = added_row['ADDRESS'].values
                if new_addrs:
                    print(f'\tadded address: {new_addrs[0]}')
        
        # concatenate modified pluto and the added data
        pluto_conc = pd.concat([pluto_update, df_added], ignore_index=True)
        
        ### handle datetime exceptions
        def int_to_datetime(date):
            if type(date) == int:
                return pd.to_datetime(date)
            elif type(date) == pd._libs.tslibs.timestamps.Timestamp:
                return date
            else:
                return 'nan'
        
        pluto_conc['SALE DATE'] = pluto_conc['SALE DATE'].apply(lambda x: int_to_datetime(x))
        
        pluto_conc = pluto_conc.sort_values(by='SALE DATE', ascending=False) \
                               .reset_index(drop=True)

        return pluto_conc

    ### fill in missed location data into the merged PLUTO
    def fill_loc(self, pluto_update):
        d_subm = dict(zip(pluto_update['ADDRESS'], pluto_update['REIS Submarket']))
        d_city = dict(zip(pluto_update['ADDRESS'], pluto_update['CITY']))
        d_state = dict(zip(pluto_update['ADDRESS'], pluto_update['STATE']))
        d_zip = dict(zip(pluto_update['ADDRESS'], pluto_update['ZIP']))
        
        p_subm = pd.DataFrame(d_subm.items(), columns=['ADDRESS', 'REIS Submarket'])
        p_city = pd.DataFrame(d_city.items(), columns=['ADDRESS', 'CITY'])
        p_state = pd.DataFrame(d_state.items(), columns=['ADDRESS', 'STATE'])
        p_zip = pd.DataFrame(d_zip.items(), columns=['ADDRESS', 'ZIP'])
        
        p_all = p_subm
        ps = [p_city, p_state, p_zip]

        for p_one in ps:
            p_all = pd.merge(p_all, p_one, on='ADDRESS', how='left')
        
        valid_cols = pluto_update.columns.difference(['REIS Submarket', 'CITY', 'STATE', 'ZIP'])
        pluto_loc_updated = pluto_update[valid_cols]
        
        pluto_loc_updated = pd.merge(pluto_loc_updated, p_all, on='ADDRESS', how='left')
        
        return pluto_loc_updated

    ### do all the data processing for PLUTO
    def process_PLUTO(self, pluto_update, instructions):
        pluto_loc = self.fill_loc(pluto_update)

        drop_index = pluto_loc[pluto_loc['BLDG CAT']=='Commercial'].index.tolist() + \
                     pluto_loc[pluto_loc['BLDG CAT']=='Industrial'].index.tolist() + \
                     pluto_loc[pluto_loc['BLDG CAT']=='Vacant Land'].index.tolist() + \
                     pluto_loc[pluto_loc['BLDG CODE']=='RESI CONDO'].index.tolist() + \
                     pluto_loc[pluto_loc['BLDG CODE']=='ROW W/OFF STORE'].index.tolist() + \
                     pluto_loc[pluto_loc['LAND SF']==0].index.tolist() + \
                     pluto_loc[pluto_loc['GSF']<800].index.tolist() + \
                     pluto_loc[pluto_loc['SALE PRICE']<25000].index.tolist()
        
        PHL_PLUTO_PROCESS = instructions['PHL_PLUTO_PROCESS']
        
        pluto_process = pluto_loc.drop(drop_index) \
                                 .reset_index(drop=True)
        
        mod_keys = list(PHL_PLUTO_PROCESS.keys())
        
        for key in mod_keys:
            mod = PHL_PLUTO_PROCESS[key]
            pluto_process.at[pluto_process[pluto_process['BLDG CODE']==key].index, 
                             ['# UNITS', 'CONDO', 'BUILDING', 'UNIT']] \
                        = [mod['# UNITS'], mod['CONDO'], mod['BUILDING'], mod['UNIT']]
        
        return pluto_process.reset_index(drop=True)

    def download_df(self):
        # API based data fetching
        API = 'https://phl.carto.com:443/api/v2/sql?q=select * from phl.opa_properties_public'.replace(' ', '%20')
        df = pd.read_json(API)
        return df

    def load_old_PLUTO(self, pluto_path):
        fn_pluto = 'PHLPL-001 All_Properties [byaddress;location] PLUTO.csv'
        pluto = pd.read_csv(f'{pluto_path}/{fn_pluto}')
        return pluto

    def export_data(self, data, exp_path, file_name):
        data.to_csv(f'{exp_path}/{file_name}')
        
    def logger(self, func, instructions):
        func_name = func.__name__
        PHL_LOGGING = instructions['PHL_LOGGING']
        print(PHL_LOGGING[func_name])
    
    ### all-in-one pipeline function to handle all the processing tasks
    def pipeline(self, pluto_path, export_path, instructions):
        warnings.simplefilter(action='ignore')

        self.logger(self.download_df, instructions)
        df = self.download_df()
        
        self.logger(self.pre_clean_df, instructions)
        df_new = self.pre_clean_df(df, instructions)
        
        self.logger(self.subset_df_date, instructions)
        df_sub = self.subset_df_date(df_new, '40 days')

        self.logger(self.export_data, instructions)
        self.export_data(df_sub, export_path, f'PHL PLUTO Monthly {date.today()}.csv')
        
        self.logger(self.load_old_PLUTO, instructions)
        pluto = self.load_old_PLUTO(pluto_path)
        
        self.logger(self.update_PLUTO, instructions)
        p = self.update_PLUTO(pluto, df_sub)
        print(f'\t->pre-processed PLUTO df shape: {p.shape}')
        
        self.logger(self.process_PLUTO, instructions)
        pnew = self.process_PLUTO(p, instructions)
        print(f'\t->post-processed PLUTO df shape: {pnew.shape}')
        
        self.logger(self.export_data, instructions)
        self.export_data(pnew, export_path, 'PHLPL-001 All_Properties [byaddress;location] PLUTO.csv')

class my_soup:

    def __init__(self):
        pass

    def _random_user_agent(self):
        """
        A helper function to generate a random header to 
        avoid getting blocked by the website

        Parameters
        ----------
        None

        Returns
        -------
        str
        a random user agent 

        >>> _random_user_agent()
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/58.0.3029.110 Safari/537.36'
        """
        try:
            ua = UserAgent()
            return ua.random
        except:
            default_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/58.0.3029.110 Safari/537.36'
            return default_ua

    def _get_soup(self, url):
        

        """
        This is a helper function that will automatically generate a 
        BeautifulSoup object based on the given URL of the apartment 
        webpage

        Parameters
        ----------
        url : str
            the URL of a specific apartment or a general website 

        Returns
        -------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage
        """

        # generate a random header 
        headers = {'User-Agent': self._random_user_agent()}
        # send a request and get the soup
        response = requests.get(url, headers=headers)
        results = response.content
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
        return soup

    def soup_attempts(self, url, total_attempts=5):

        """
        A helper function that will make several attempts
        to obtain a soup to avoid getting blocked

        Parameters
        ----------
        url : str
            the URL of a specific apartment or a general website 

        total_attempts: int
            the number of attempts you want to try to obtain the 
            soup before you already give up. Default is 5 attempts

        Returns
        -------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage        

        """

        soup = self._get_soup(url)

        # if we get the soup with the first attempt
        if soup:
            return soup
        # if we don't get the soup during our first
        # attempt
        else:
            attempts = 0
            while attempts < total_attempts:
                # put the program idle to avoid detection
                time.sleep(3)
                soup = self._get_soup(url)
                if soup:
                    return soup
            # time to give up, try to find what's going on 
            raise ValueError(f'FAILED to get soup for apt url {url}')

class nyc_cleaning_pipeline(my_soup):

    def __init__(self):
        super()
        self._nyc_sales_page = 'https://www1.nyc.gov/site/finance/taxes/property-rolling-sales-data.page'
        self._nyc_pluto_page = 'https://www1.nyc.gov/site/planning/data-maps/open-data/dwn-pluto-mappluto.page'

    def _extract_sales_data(self):
        soup = self.soup_attempts(self._nyc_sales_page)
        
        # not looking at Statan Island
        statan = 'statenisland'

        finance_table = soup.find('table', class_='finance rolling_sales')

        all_links = [link['href'] for link in finance_table.find_all('a')]
        valid_links = [f'http://www1.nyc.gov{l}' for l in all_links if (statan not in l) and ('.pdf' not in l)]

        dfs = []
        
        for link in valid_links:
            df = pd.read_excel(link, header=4) # column names appear starting from row 5
            dfs.append(df)

        # this is the sales data in raw format
        df_sm = pd.concat(dfs, axis=0, ignore_index=True)

        return df_sm

    def _clean_sales_data(self, df_sm, instructions):
        ins = instructions['NYC_SALES_CLEANING']

        orig_cols = list(ins.keys()) # original column names to be updated 
        df_smcl = df_sm.copy()[orig_cols] # sales data cleaned 
        
        for column in orig_cols:
            if ins[column]['delete'] == 1:
                df_smcl = df_smcl.drop([column], axis=1)
            if ins[column]['delete'] == 0:
                df_smcl = df_smcl.rename(columns={column: ins[column]['new name']})
        
        df_smcl = df_smcl.reindex(df_smcl.columns.tolist(), axis=1) \
                         .astype(dtype={'SALE DATE': str})
        
        df_smcl['SALE DATE'] = pd.to_datetime(df_smcl['SALE DATE'])
        df_smcl = df_smcl.sort_values(by=['SALE DATE'], ascending=False) \
                         .reset_index(drop=True)

        return df_smcl

    def _process_sales_data(self, df_smcl):

        drop_index = df_smcl[df_smcl['APT #']=='#'].index.tolist() + \
                     df_smcl[df_smcl['GSF']<850].index.tolist() + \
                     df_smcl[df_smcl['LAND SF']==0].index.tolist() + \
                     df_smcl[df_smcl['SALE PRICE']<25000].index.tolist() + \
                     df_smcl[df_smcl['BLDG CLASS'].isin([
                        'A8', 'C6', 'C8', 'C9', 'CM', 'D', 'E', 'F',
                        'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 
                        'P', 'Q', 'R', 'T', 'U', 'V', 'W', 'Y', 'Z'])].index.tolist()

        df_smps = df_smcl.drop(drop_index).reset_index(drop=True)
        df_smps['ADDRESS'] = df_smps['ADDRESS'].astype(str)

        cleaner = Address_cleaner()
        df_smps['ADDRESS'] = cleaner.easy_clean(df_smps['ADDRESS'].str.upper())

        def remove_units(address):
            if ', ' in address:
                address = address.split(', ')[0].strip()
            return address

        df_smps['ADDRESS'] = df_smps['ADDRESS'].apply(remove_units)
        return df_smps

    def pipeline_sales_data(self, instructions):
        df_sm = self._extract_sales_data() # extract sales data
        df_smcl = self._clean_sales_data(df_sm, instructions) # clean sales data
        df_smps = self._process_sales_data(df_smcl) # process sales data 
        return df_smps

    def _extract_new_pluto(self):
        soup = self.soup_attempts(self._nyc_pluto_page)
        textbox = soup.find_all('div', class_='text-box')
        links = [l['href'] for tb in textbox for l in tb.find_all('a')]

        pluto_link = [f'http://www1.nyc.gov{l}' \
                        for l in links \
                            if ('nyc_pluto' in l) \
                            and ('csv.zip' in l)][0]

        resp = urlopen(pluto_link)
        zipfile = ZipFile(BytesIO(resp.read()))
        
        fn_pluto = [fn for fn in zipfile.namelist() \
                        if ('pluto' in fn) and ('.csv' in fn)][0]
        df_plu = pd.read_csv(zipfile.open(fn_pluto), low_memory=False)
        return df_plu

    def _clean_new_pluto(self, df_plu, instructions):
        ins = instructions['NYC_PLUTO_CLEANING']

        orig_cols = list(ins.keys()) # original column names to be updated 
        df_plucl = df_plu.copy()[orig_cols] # sales data cleaned 
        
        for column in orig_cols:
            if ins[column]['delete'] == 1:
                df_plucl = df_plucl.drop([column], axis=1)
            if ins[column]['delete'] == 0:
                df_plucl = df_plucl.rename(columns={column: ins[column]['new name']})
        
        df_plucl['REIS SUBMARKET'] = ''

        return df_plucl

    def _process_new_pluto(self, df_plucl):
        drop_index = df_plucl[df_plucl['BLDG CLASS NOW'].isin([
                        'A8', 'C6', 'C8', 'C9', 'CM', 'D', 'E',
                        'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
                        'N', 'O', 'P', 'Q', 'R', 'T', 'U', 'V',
                        'W', 'Y', 'Z'])].index.tolist() + \
                     df_plucl[df_plucl['GSF']<800].index.tolist() + \
                     df_plucl[df_plucl['# FLOORS']==0].index.tolist() + \
                     df_plucl[df_plucl['# UNITS']==0].index.tolist()

        df_plups = df_plucl.drop(drop_index).reset_index(drop=True)
        df_plups['ADDRESS'] = df_plups['ADDRESS'].astype(str)

        cleaner = Address_cleaner()
        df_plups['ADDRESS'] = cleaner.easy_clean(df_plups['ADDRESS'].str.upper())

        return df_plups

    def pipeline_new_pluto(self, instructions): 
        df_plu = self._extract_new_pluto()
        df_plucl = self._clean_new_pluto(df_plu, instructions)
        df_plups = self._process_new_pluto(df_plucl)
        return df_plups

    ### this step should be only done once 
    def _load_old_pluto(self, pluto_path, fn_opluto):
        fn_old_pluto = 'NPL-001 All_Properties [bylocation;address] PLUTO.csv'
        fn_sales_master = 'NMA-002 Resi_Sales_Master [bylocation;addresses].csv'

        fn_core_pluto = 'NPL-001 All_Properties [bylocation;address] PLUTO Core.csv'

        if (not os.path.exists(f'{pluto_path}/{fn_core_pluto}')) or (fn_opluto==''):
            df_pluto = pd.read_csv(f'{pluto_path}/{fn_old_pluto}', index_col=0, low_memory=False)
            df_sales = pd.read_csv(f'{pluto_path}/{fn_sales_master}', index_col=0, low_memory=False)

            df_sales['SALE DATE'] = pd.to_datetime(df_sales['SALE DATE'])

            df_pluto = df_pluto.drop_duplicates(subset=['ADDRESS', 'BLOCK', 'LOT', '# UNITS'])

            # for multiple properties with identical address, block, lot and  units
            # we know they are the same property and thus only the most recent 
            # property details are kept            
            df_sales = df_sales.sort_values(by='SALE DATE') \
                               .drop_duplicates(subset=['ADDRESS', 'BLOCK', 'LOT', '# UNITS'], 
                                                keep='last')

            df_pluto_core = pd.merge(df_pluto, 
                                     df_sales, 
                                     on=['ADDRESS', 'BLOCK', 'LOT', '# UNITS'],
                                     how='outer')

            all_cols = df_pluto_core.columns
            dup_cols = [col for col in all_cols if '_y' in col]
            df_pluto_core = df_pluto_core[all_cols.difference(dup_cols)] \
                                 .rename(columns={col: col.strip('_x') for col in all_cols if '_x' in col}) \
                                 .reset_index(drop=True)

            df_pluto_core.to_csv(f'{pluto_path}/{fn_core_pluto}')

            return df_pluto_core

        else:
            df_pluto_old = pd.read_csv(f'{pluto_path}/{fn_opluto}', index_col=0, low_memory=False)
            return df_pluto_old

    def _update_pluto_with_df(self, pluto_old, df_new, cols_id=['ADDRESS', 'BLOCK', 'LOT', '# UNITS']):
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

    def _load_reis(self, reis_path):
        reis = pd.read_excel(f'{reis_path}/REIS All Properties 152k Report.xlsx')
        return reis

    def _clean_reis(self, reis, instructions):
        ins = instructions['NYC_REIS_RENAME']
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

    def pipeline_reis_data(self, reis_path, instructions):
        reis = self._load_reis(reis_path)
        reis_cl = self._clean_reis(reis, instructions)
        return reis_cl

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
                             .drop_duplicates(subset=['ADDRESS', 'BLOCK', 'LOT', '# UNITS'], 
                                              keep='last')

        final_pluto = self._update_pluto_with_df(pluto, sales_sub)

        return final_pluto

    ### fill in missed location data into the merged PLUTO
    def _fill_loc(self, pluto_update):
        d_subm = dict(zip(pluto_update['ADDRESS'], pluto_update['REIS SUBMARKET']))
        d_zip = dict(zip(pluto_update['ADDRESS'], pluto_update['ZIP']))
        
        p_subm = pd.DataFrame(d_subm.items(), columns=['ADDRESS', 'REIS SUBMARKET'])
        p_zip = pd.DataFrame(d_zip.items(), columns=['ADDRESS', 'ZIP'])
        
        p_all = pd.merge(p_subm, p_zip, on='ADDRESS', how='left')
        
        valid_cols = pluto_update.columns.difference(['REIS SUBMARKET', 'ZIP'])
        pluto_loc_updated = pluto_update[valid_cols]
        
        pluto_loc_updated = pd.merge(pluto_loc_updated, p_all, on='ADDRESS', how='left')
        
        return pluto_loc_updated

    ### export the final merged and most updated PLUTO 
    def _export_final_pluto(self, fpluto, fpluto_path, deltadays=40):
        fn_fpluto = 'NPL-001 All_Properties [bylocation;address] PLUTO'
        fpluto_final = self._fill_loc(fpluto).reset_index(drop=True)
        fpluto_final['SALE DATE'] = pd.to_datetime(fpluto_final['SALE DATE'])
        fpluto_final.to_csv(f'{fpluto_path}/{fn_fpluto}.csv')

        delta = pd.Timedelta(deltadays)
        fpluto_final = fpluto_final.sort_values(by=['SALE DATE'], ascending=False)
        latest_date = fpluto_final['SALE DATE'].iloc[0]
        earliest_date = latest_date-delta

        keep_index = fpluto_final[(fpluto_final['SALE DATE']>=earliest_date) & 
                                  (fpluto_final['SALE DATE']<=latest_date)].index.tolist()

        pluto_monthly = fpluto_final.iloc[keep_index].reset_index(drop=True)
        pluto_monthly.to_csv(f'{output_path}/NPL PLUTO Monthly {date.today()}.csv')

    ### the entire pipeline to process PLUTO 
    def pipeline(self, instructions, pluto_path, reis_path, fpluto_path, fn_opluto=''):
        # old pluto data loaded
        print('>>> Processing and loading old PLUTO')
        df_opluto = self._load_old_pluto(pluto_path, fn_opluto)
        print(f'-> Original PLUTO shape: {df_opluto.shape}')

        # new pluto data processed 
        print('>>> Downloading, cleaning and processing new PLUTO')
        df_npluto = self.pipeline_new_pluto(instructions)
        print(f'-> New PLUTO shape: {df_npluto.shape}')

        # old pluto data updated with new pluto data
        print('>>> Updating old PLUTO with new PLUTO')
        df_upluto = self._update_pluto_with_df(df_opluto, df_npluto)
        df_upluto['ZIP'] = df_upluto['ZIP'].astype(int, errors='ignore')
        print(f'-> PLUTO shape: {df_upluto.shape}')

        print('>>> Loading and processing REIS')
        df_reis = self.pipeline_reis_data(reis_path, instructions)
        print(f'-> REIS shape: {df_reis.shape}')

        print('>>> Updating PLUTO with REIS')
        df_rpluto = self._update_pluto_with_df(df_upluto, df_reis, cols_id=['ADDRESS', 'ZIP'])
        print(f'-> PLUTO shape: {df_rpluto.shape}')

        # new sales data processed
        print('>>> Downloading, cleaning and processing new sales data')
        df_nsales = self.pipeline_sales_data(instructions)
        print(f'-> Sales Data shape: {df_nsales.shape}')

        # final pluto updated by the latest sales data
        print('>>> Updating PLUTO with recent sales data')
        final_pluto = self._update_pluto_with_sales_data(df_rpluto, df_nsales, 40)
        print(f'-> PLUTO shape: {final_pluto.shape}')

        print('>>> Exporting final PLUTO')
        self._export_final_pluto(final_pluto, fpluto_path)
        print('>>> job done! Congratulations!')

class chi_cleaning_pipeline:

    def __init__(self):
        self._chi_pluto_api_id = 'bcnq-qi2z'
        self._chi_sales_api_id = '5pge-nu6u'

    ### extract data from API 
    def _extract_data(self, api_id):
        MAX_LIMIT = 1000000000
        # MAX_LIMIT = 10000
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
                               .drop_duplicates(subset=['PIN', 'ADDRESS', 'BLDG CODE', 'LAND SF'], 
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

    def _clean_reis(self, reis, ins):
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

    def pipeline_reis_data(self, reis_path, ins):
        reis = self._load_reis(reis_path)
        reis_cl = self._clean_reis(reis, ins)
        return reis_cl

    def _process_pluto(self, pluto, ins):
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

        # if the number is an integer, we should remove all the '.0', if it's a float, leave it as is 
        for col in pcols:
            pluto_final[col] = pluto_final[col].apply(lambda x: str(x).split('.')[0] if float(x).is_integer() else str(x))

        # map the values to the corresponding values in WHITEROCK 
        # use .fillna for Non-Exhaustive Mapping
        pluto_final['GARAGE ATTACHED'] = pluto_final['GARAGE ATTACHED'].map(ins['GARAGE ATTACHED']).fillna(pluto_final['GARAGE ATTACHED'])
        pluto_final['GARAGE 1 AREA'] = pluto_final['GARAGE 1 AREA'].map(ins['GARAGE 1 AREA']).fillna(pluto_final['GARAGE 1 AREA'])
        pluto_final['GARAGE 1'] = pluto_final['GARAGE 1'].map(ins['GARAGE 1']).fillna(pluto_final['GARAGE 1'])
        pluto_final['BLDG CODE DEF'] = pluto_final['BLDG CODE'].map(ins['BLDG CODE']).fillna(pluto_final['BLDG CODE DEF'])
        pluto_final['# FLOORS'] = pluto_final['BLDG CAT'].map(ins['BLDG CAT']).fillna(pluto_final['# FLOORS'])

        pluto_final = pluto_final.reset_index(drop=True)

        # Process the YEAR BUILT: substract the current year from the year in the original df 
        pluto_final['YEAR BUILT'] = pluto_final['YEAR BUILT'].astype(float)

        # select the year that is not NaN and process it 
        idx = pluto_final[~pluto_final['YEAR BUILT'].isnull()].index
        pluto_final['YEAR BUILT'].iloc[idx] = pluto_final['YEAR BUILT'].iloc[idx].astype(int)

        # subtract the current year from the year in the original data
        current_year = int(date.today().year)
        pluto_final['YEAR BUILT'].iloc[idx] = current_year-pluto_final['YEAR BUILT'].iloc[idx]
        pluto_final['YEAR BUILT'].iloc[idx] = pluto_final['YEAR BUILT'].iloc[idx].astype(int)

        pluto_final = pluto_final.reset_index(drop=True)
        
        return pluto_final

    def _export_pluto(self, pluto_final, output_path, deltadays=40):
        pluto_final['SALE DATE'] = pd.to_datetime(pluto_final['SALE DATE'])
        pluto_final.to_csv(f'{output_path}/CHIPL-001 All_Properties PLUTO.csv')

        delta = pd.Timedelta(deltadays)
        pluto_final = pluto_final.sort_values(by=['SALE DATE'], ascending=False)
        latest_date = pluto_final['SALE DATE'].iloc[0]
        earliest_date = latest_date-delta

        keep_index = pluto_final[(pluto_final['SALE DATE']>=earliest_date) & 
                                 (pluto_final['SALE DATE']<=latest_date)].index.tolist()

        pluto_monthly = pluto_final.iloc[keep_index].reset_index(drop=True)
        pluto_monthly.to_csv(f'{output_path}/CHIPL PLUTO Monthly {date.today()}.csv')

    def pipeline(self, ins, pluto_path, reis_path, ouput_path):
        print('>>> Downloanding and cleaning sales data, takes a while')
        sales_data = self.pipeline_data(self._chi_sales_api_id, ins['CHI_SALES_CLEANING'])
        print(f'-> Sales data shape: {sales_data.shape}')

        print('>>> Downloading and cleaning new PLUTO, takes a while, please be patient')
        pluto_new = self.pipeline_data(self._chi_pluto_api_id, ins['CHI_PLUTO_CLEANING'])
        print(f'-> New PLUTO shape: {pluto_new.shape}')

        print('>>> Loading and cleaning old PLUTO')
        pluto_old = self._load_old_pluto(pluto_path)
        print(f'-> Old PLUTO shape: {pluto_old.shape}')

        print('>>> Updating old PLUTO with new PLUTO')
        pluto_stage1 = self._update_pluto_with_df(pluto_old, pluto_new)
        print(f'-> [Stage 1] PLUTO shape: {pluto_stage1.shape}')

        print('>>> Updating [stage 1] PLUTO with sales data')
        pluto_stage2 = self._update_pluto_with_sales_data(pluto_stage1, sales_data, 40)
        print(f'-> [Stage 2] PLUTO shape: {pluto_stage2.shape}')

        print('>>> Loading and cleaning REIS')
        reis = self.pipeline_reis_data(reis_path, instructions['CHI_REIS_RENAME'])
        print(f'-> REIS shape: {reis.shape}')

        print('>>> Updating [stage 2] PLUTO with REIS')
        pluto_stage3 = self._update_pluto_with_df(pluto_stage2, reis, cols_id=['ADDRESS'])
        print(f'-> [Stage 3] PLUTO shape: {pluto_stage3.shape}')

        print('>>> Processing [final stage] PLUTO')
        pluto_final = self._process_pluto(pluto_stage3, instructions['CHI_COL_MAPPING'])
        print(f'-> Final PLUTO shape: {pluto_final.shape}')

        print('>>> Exporting final PLUTO')
        self._export_pluto(pluto_final, output_path)

        print('>>> Job Done! Congratulations!')

### Google API image downloading class
class PicDownloader:

    def __init__(self):
        self.key  = "AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE"

    def searching_from_pluto(self, pluto, address, target):
        return pluto[pluto['ADDRESS'] == address][target].values[0]
        
    def download(self, url, name):
        urllib.request.urlretrieve(url.replace(" ", "%20"),"%s.png" % name)

    def gen_url(self, geom, fov=100, heading=0, pitch=30, size=(500, 500)):
        x, y = size
        lat, lng = geom
        return "https://maps.googleapis.com/maps/api/streetview?size=%s" \
                "x%s&location=%s,%s&fov=%s&heading=%s&pitch=%s" \
                "&key=AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE" \
                % (x, y, lat, lng, fov, heading, pitch)

    def gen_url_by_string(self, address, fov=60, pitch=30, size=(400, 400)):
        x, y = size
        return "https://maps.googleapis.com/maps/api/streetview?size=%sx" \
                "%s&location=%s&fov=%s&pitch=%s" \
                "&key=AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE" \
                % (x, y, address, fov, pitch)

    def address_checker(self, address, pic_path, folders):

        addr_exist = False

        for folder in folders:
            if os.path.exists(f'{pic_path}/{folder}/{address}.png'):
                addr_exist = True

        return addr_exist

    def export_addr_img(self, city, data, pic_path, saving_dir, folders):

        address_list = list(set(list(data.dropna(subset=['ADDRESS'])['ADDRESS'].values)))

        for address in address_list:
            try:
                new_addr = '_'.join(address.split('/')) + ', ' + city
                new_addr_pic = '_'.join(address.split('/'))
                
                addr_exist = self.address_checker(new_addr, pic_path, folders)    

                if (not addr_exist) and new_addr[0].isnumeric():
                    url = self.gen_url_by_string(new_addr)
                    saving_path = f'{saving_dir}/{new_addr}'
                    self.download(url, saving_path)
                    time.sleep(5)
                
            except Exception as e:
                print(e)
                print(str(address_list.index(address)))
                new_addr = '_'.join(address.split('/')) + ', ' + city
                new_addr_pic = '_'.join(address.split('/'))
                pass

if __name__ == '__main__':

    instructions = ci.instructions

    ### NYC PLUTO Update
    print(f'NYC PLUTO UPDATE START!')
    nyc_data_path, nyc_reis_data, nyc_export_path = '../../data/NYC Data', '../../data/NYC Data', '../../data'
    ncp = nyc_cleaning_pipeline()
    ncp.pipeline(instructions, nyc_data_path, nyc_reis_data, nyc_export_path)

    ### CHI PLUTO Update 
    print(f'CHI PLUTO UPDATE START!')
    chi_data_path, chi_reis_data, chi_export_path = '../../data/CHI Data', '../../data/CHI Data', '../../data'
    ccp = chi_cleaning_pipeline()
    ccp.pipeline(instructions, chi_data_path, chi_reis_data, chi_export_path)

    ### PHL PLUTO Update 
    print(f'PHL PLUTO UPDATE START!')
    phl_data_path, phl_export_path = '../../data/PHL Data', '../../data'
    pcp = phl_cleaning_pipeline()
    pcp.pipeline(instructions, phl_data_path, phl_export_path, instructions)
