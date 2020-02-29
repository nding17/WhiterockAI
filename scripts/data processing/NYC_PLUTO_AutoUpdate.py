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
from bs4 import BeautifulSoup
from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
from lycleaner import Address_cleaner

class cleaning_instructions:

    NYC_SALES_CLEANING = {
        'BOROUGH': {
            'delete': 0,
            'new name': 'BOROUGH',
        },
        'NEIGHBORHOOD': {
            'delete': 0,
            'new name': 'NEIGHBORHOOD',
        },
        'BUILDING CLASS CATEGORY': {
            'delete': 1,
        },
        'TAX CLASS AT PRESENT': {
            'delete': 0,
            'new name': 'TAX CLASS',
        },
        'BLOCK': {
            'delete': 0,
            'new name': 'BLOCK',
        },
        'LOT': {
            'delete': 0,
            'new name': 'LOT',
        },
        'EASE-MENT': {
            'delete': 1
        },
        'BUILDING CLASS AT PRESENT': {
            'delete': 0,
            'new name': 'BLDG CLASS',
        },
        'ADDRESS': {
            'delete': 0,
            'new name': 'ADDRESS',
        },
        'APARTMENT NUMBER': {
            'delete': 0,
            'new name': 'APT #',
        },
        'ZIP CODE': {
            'delete': 0,
            'new name': 'ZIP',
        },
        'RESIDENTIAL UNITS': {
            'delete': 0,
            'new name': 'RESI UNITS',
        },
        'COMMERCIAL UNITS': {
            'delete': 0,
            'new name': 'COMM UNITS',
        },
        'TOTAL UNITS': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'LAND SQUARE FEET': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'GROSS SQUARE FEET': {
            'delete': 0,
            'new name': 'GSF',
        },
        'YEAR BUILT': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'TAX CLASS AT TIME OF SALE': {
            'delete': 0,
            'new name': 'TAX CLASS SALE',
        },
        'BUILDING CLASS AT TIME OF SALE': {
            'delete': 0,
            'new name': 'CLASS SALE',
        },
        'SALE PRICE': {
            'delete': 0,
            'new name': 'SALE PRICE',
        },
        'SALE DATE': {
            'delete': 0,
            'new name': 'SALE DATE',
        },
    }

    NYC_PLUTO_CLEANING = {
        'borough': {
            'delete': 0,
            'new name': 'BOROUGH',
        },
        'block': {
            'delete': 0,
            'new name': 'BLOCK',
        },
        'lot': {
            'delete': 0,
            'new name': 'LOT',
        },
        'cd': {
            'delete': 1,
        },
        'ct2010': {
            'delete': 1,
        },
        'cb2010': {
            'delete': 1,
        },
        'schooldist': {
            'delete': 0,
            'new name': 'SCHOOL DIS',
        },
        'council': {
            'delete': 0,
            'new name': 'COUNCIL',
        },
        'zipcode': {
            'delete': 0,
            'new name': 'ZIP',
        },
        'firecomp': {
            'delete': 0,
            'new name': 'FIRE COMP',
        },
        'policeprct': {
            'delete': 0,
            'new name': 'POLICE PRCT',
        },
        'healtharea': {
            'delete': 0,
            'new name': 'HEALTH AREA',
        },
        'sanitboro': {
            'delete': 0,
            'new name': 'SANIT BORO',
        },
        'sanitsub': {
            'delete': 1,
        },
        'address': {
            'delete': 0,
            'new name': 'ADDRESS',
        },
        'zonedist1': {
            'delete': 0,
            'new name': 'zonedist1',
        },
        'zonedist2': {
            'delete': 0,
            'new name': 'zonedist2',
        },
        'zonedist3': {
            'delete': 0,
            'new name': 'zonedist3',
        },
        'zonedist4': {
            'delete': 0,
            'new name': 'zonedist4',
        },
        'overlay1': {
            'delete': 0,
            'new name': 'overlay1',
        },
        'overlay2': {
            'delete': 0,
            'new name': 'overlay2',
        },
        'spdist1': {
            'delete': 0,
            'new name': 'spdist1',
        },
        'spdist2': {
            'delete': 0,
            'new name': 'spdist2',
        },
        'spdist3': {
            'delete': 0,
            'new name': 'spdist3',
        },
        'ltdheight': {
            'delete': 1,
        },
        'splitzone': {
            'delete': 1,
        },
        'bldgclass': {
            'delete': 0,
            'new name': 'BLDG CLASS NOW',
        },
        'landuse': {
            'delete': 0,
            'new name': 'LAND USE',
        },
        'easements': {
            'delete': 0,
            'new name': 'easements',
        },
        'ownertype': {
            'delete': 0,
            'new name': 'OWNER TYPE',
        },
        'ownername': {
            'delete': 0,
            'new name': 'OWNER',
        },
        'lotarea': {
            'delete': 0,
            'new name': 'LAND SF',
        },
        'bldgarea': {
            'delete': 0,
            'new name': 'GSF',
        },
        'comarea': {
            'delete': 0,
            'new name': 'COMM SF',
        },
        'resarea': {
            'delete': 0,
            'new name': 'RESI SF',
        },
        'officearea': {
            'delete': 0,
            'new name': 'OFFICE SF',
        },
        'retailarea': {
            'delete': 0,
            'new name': 'RETAIL SF',
        },
        'garagearea': {
            'delete': 0,
            'new name': 'GARAGE SF',
        },
        'strgearea': {
            'delete': 0,
            'new name': 'STORAGE SF',
        },
        'factryarea': {
            'delete': 0,
            'new name': 'FACTORY SF',
        },
        'otherarea': {
            'delete': 0,
            'new name': 'OTHER SF',
        },
        'areasource': {
            'delete': 1,
        },
        'numbldgs': {
            'delete': 0,
            'new name': '# BLDG',
        },
        'numfloors': {
            'delete': 0,
            'new name': '# FLOORS',
        },
        'unitsres': {
            'delete': 1,
        },
        'unitstotal': {
            'delete': 0,
            'new name': '# UNITS',
        },
        'lotfront': {
            'delete': 0,
            'new name': 'LOT FRONT',
        },
        'lotdepth': {
            'delete': 0,
            'new name': 'LOT DEPTH',
        },
        'bldgfront': {
            'delete': 0,
            'new name': 'BLDG FRONT',
        },
        'bldgdepth': {
            'delete': 0,
            'new name': 'BLDG DEPTH',
        },
        'ext': {
            'delete': 1,
        },
        'proxcode': {
            'delete': 1,
        },
        'irrlotcode': {
            'delete': 1, 
        },
        'lottype': {
            'delete': 0,
            'new name': 'LOT TYPE',
        },
        'bsmtcode': {
            'delete': 0,
            'new name': 'bsmtcode',
        },
        'assessland': {
            'delete': 0,
            'new name': 'assessland',
        },
        'assesstot': {
            'delete': 0,
            'new name': 'assesstot',
        },
        'exempttot': {
            'delete': 0,
            'new name': 'exempttot',
        },
        'yearbuilt': {
            'delete': 0,
            'new name': 'YEAR BUILT',
        },
        'yearalter1': {
            'delete': 0,
            'new name': 'yearalter1',
        },
        'yearalter2': {
            'delete': 0,
            'new name': 'yearalter2',
        },
        'histdist': {
            'delete': 1,
        },
        'landmark': {
            'delete': 1,
        },
        'builtfar': {
            'delete': 0,
            'new name': 'builtfar',
        },
        'residfar': {
            'delete': 0,
            'new name': 'residfar',
        },
        'commfar': {
            'delete': 0,
            'new name': 'commfar',
        },
        'facilfar': {
            'delete': 0,
            'new name': 'facilfar',
        },
        'borocode': {
            'delete': 1,
        },
        'bbl': {
            'delete': 1,
        },
        'condono': {
            'delete': 1,
        },
        'tract2010': {
            'delete': 1,
        },
        'xcoord': {
            'delete': 1,
        },
        'ycoord': {
            'delete': 1,
        },
        'latitude': {
            'delete': 0,
            'new name': 'LATITUDE',
        },
        'longitude': {
            'delete': 0,
            'new name': 'LONGITUDE',
        },
        'zonemap': {
            'delete': 1,
        },
        'zmcode': {
            'delete': 1,
        },
        'sanborn': {
            'delete': 1
        },
        'taxmap': {
            'delete': 1
        },
        'edesignum': {
            'delete': 0,
            'new name': 'edesignum',
        },
        'appbbl': {
            'delete': 0,
            'new name': 'appbbl',
        },
        'appdate': {
            'delete': 1,
        },
        'plutomapid': {
            'delete': 1,
        },
        'version': {
            'delete': 1,
        },
        'sanitdistrict': {
            'delete': 0,
            'new name': 'sanitdistrict',
        },
        'healthcenterdistrict': {
            'delete': 0,
            'new name': 'healthcenterdistrict',
        },
        'firm07_flag': {
            'delete': 0,
            'new name': 'firm07_flag',
        },
        'pfirm15_flag': {
            'delete': 0,
            'new name': 'pfirm15_flag',
        },
        'rpaddate': {
            'delete': 1,
        },
        'dcasdate': {
            'delete': 1,
        },
        'zoningdate': {
            'delete': 1,
        },
        'landmkdate': {
            'delete': 1,
        },
        'basempdate': {
            'delete': 1,
        },
        'masdate': {
            'delete': 1,
        },
        'polidate': {
            'delete': 1,
        },
        'edesigdate': {
            'delete': 0,
            'new name': 'edesigdate',
        },
        'geom': {
            'delete': 1,
        },
        'dcpedited': {
            'delete': 1,
        },
        'notes': {
            'delete': 1,
        },
    }

    instructions = {
        'NYC_SALES_CLEANING': NYC_SALES_CLEANING,
        'NYC_PLUTO_CLEANING': NYC_PLUTO_CLEANING,
    }

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

class cleaning_pipeline(my_soup):

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

    def _clean_sales_data(self, df_sm):
        cl = cleaning_instructions() # cleaning instructions for sales data
        ins = cl.instructions['NYC_SALES_CLEANING']

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

        return df_smps

    def pipeline_sales_data(self):
        df_sm = self._extract_sales_data() # extract sales data
        df_smcl = self._clean_sales_data(df_sm) # clean sales data
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

    def _clean_new_pluto(self, df_plu):
        cl = cleaning_instructions() # cleaning instructions for sales data
        ins = cl.instructions['NYC_PLUTO_CLEANING']

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

    def pipeline_new_pluto(self): 
        df_plu = self._extract_new_pluto()
        df_plucl = self._clean_new_pluto(df_plu)
        df_plups = self._process_new_pluto(df_plucl)
        return df_plups

    ### this step should be only done once 
    def _load_old_pluto(self, pluto_path, fn_opluto):
        fn_old_pluto = 'NPL-001 All_Properties [bylocation;address] PLUTO.csv'
        fn_sales_master = 'NMA-002 Resi_Sales_Master [bylocation;addresses].csv'

        fn_core_pluto = 'NPL-001 All_Properties [bylocation;address] PLUTO Core.csv'

        if (not os.path.exists(f'{pluto_path}/{fn_core_pluto}')) or (''==fn_opluto):
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

            return df_pluto

        else:
            df_pluto_old = pd.read_csv(f'{pluto_path}/{fn_opluto}', index_col=0, low_memory=False)
            return df_pluto_old

    def _update_pluto_with_df(self, pluto_old, pluto_new):
        # all the columns of the old PLUTO
        cols_op = pluto_old.columns.tolist()
        # all the columns of the new PLUTO
        cols_np = pluto_new.columns.tolist()

        # PLUTO update dataframe
        added_cols = list(set(cols_np)-set(cols_op))
        pluto_up = pd.concat([pluto_old.copy(), pd.DataFrame(columns=added_cols)], sort=False)

        # ADDRESS, BLOCK, LOT and # UNITS combined are unique identifiers of the 
        # properties in PLUTO
        id_cols = ['ADDRESS', 'BLOCK', 'LOT', '# UNITS']
        id_up = pluto_up[id_cols] # identifiers for the old PLUTO
        id_new = pluto_new[id_cols] # identifiers for the new PLUTO

        # find the same identifiers: identifiers that exist in both new and old PLUTO data
        # as well as the different identifiers that are unique in each PLUTO data
        same_id = pd.merge(id_up, id_new, how='inner', indicator=False)
        diff_id = id_new[~id_new.isin(same_id)] # diff identifiers

        print(f'{same_id.shape[0]} rows to be updated, {diff_id.shape[0]} rows to be added')

        # the index of a list of the same identifiers in the new PLUTO
        idx_sid_new = pluto_new[pluto_new[id_cols].isin(same_id)].index
        # the index of a list of the same identifiers in the old PLUTO
        idx_sid_up = pluto_up[pluto_up[id_cols].isin(same_id)].index

        # update the old PLUTO with the data in the new PLUTO
        pluto_up.at[idx_sid_up, cols_np] = pluto_new.iloc[idx_sid_new]

        # concat the updated PLUTO with new property data that's not 
        # already in the old PLUTO file
        pluto_up = pd.concat([pluto_up, pluto_new[pluto_new[id_cols].isin(diff_id)]], sort=False)

        return pluto_up

    def _update_pluto_with_sales_data(self, pluto, sales, deltadays):
        delta = pd.Timedelta(deltadays)
        sales = sales.sort_values(by=['SALE DATE'], ascending=False)
        latest_date = sales['SALE DATE'].iloc[0]
        earliest_date = latest_date-delta
        keep_index = sales[(sales['SALE DATE']>=earliest_date) & 
                           (sales['SALE DATE']<=latest_date)].index
        sales_sub = sales.iloc[keep_index].reset_index(drop=True)

        sales_sub = sales_sub.sort_values(by='SALE DATE') \
                             .drop_duplicates(subset=['ADDRESS', 'BLOCK', 'LOT', '# UNITS'], 
                                              keep='last')

        final_pluto = pd.merge(pluto, 
                               sales_sub, 
                               on=['ADDRESS', 'BLOCK', 'LOT', '# UNITS'],
                               how='outer')

        final_pluto = self._update_pluto_with_df(final_pluto, sales_sub)

        return final_pluto

    def _export_final_pluto(self, fpluto, fpluto_path):
        fn_fpluto = 'NPL-001 All_Properties [bylocation;address] PLUTO'
        fpluto.to_csv(f'{fpluto_path}/{fn_fpluto} {date.today()}.csv')

    def pipeline(self, pluto_path, fpluto_path, fn_opluto=''):
        # new sales data processed
        print('>>>downloading, cleaning and processing new sales data')
        df_nsales = self.pipeline_sales_data()

        # new pluto data processed 
        print('>>>downloading, cleaning and processing new PLUTO')
        df_npluto = self.pipeline_new_pluto()

        # old pluto data loaded
        print('>>>processing and loading old PLUTO')
        df_opluto = self._load_old_pluto(pluto_path, fn_opluto=fn_opluto)

        # old pluto data updated with new pluto data
        print('>>>updating old PLUTO with new PLUTO')
        df_upluto = self._update_pluto_with_df(df_opluto, df_npluto)

        # final pluto updated by the latest sales data
        print('>>>updating PLUTO with recent sales data')
        final_pluto = self._update_pluto_with_sales_data(df_upluto, df_nsales, 40)

        print('>>>exporting final PLUTO')
        self._export_final_pluto(final_pluto, fpluto_path)
        print('>>>job done! Congratulations!')

if __name__ == '__main__':
    cp = cleaning_pipeline()
    cp.pipeline('../../data/NYC Data', '../../data')