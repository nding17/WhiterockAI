### package requirements
import pandas as pd
import numpy as np
import warnings
import urllib
import os
import time
import requests

from datetime import datetime
from bs4 import BeautifulSoup
from tabulate import tabulate

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
            'new name': 'BLDG CLASS ',
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

    instructions = {
        'NYC_SALES_CLEANING': NYC_SALES_CLEANING,
    }

class my_soup:

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

class cleaning_pipeline:

    def __init__(self):
        self._nyc_sales_page = 'https://www1.nyc.gov/site/finance/taxes/property-rolling-sales-data.page'

    def _extract_sales_data(self):
        ms = my_soup()
        soup = ms.soup_attempts(self._nyc_sales_page)
        
        # not looking at Statan Island
        statan = 'statenisland'

        finance_table = soup.find('table', class_='finance rolling_sales')

        all_links = [link['href'] for link in finance_table.find_all('a')]
        valid_links = [f'http://www1.nyc.gov{l}' for l in all_links if (statan not in l) and ('.pdf' not in l)]

        dfs = []
        
        for link in valid_links:
            df = pd.read_excel(link, header=4) # column names appear starting from row 5
            dfs.append(df)

        df_sm = pd.concat(dfs, axis=0, ignore_index=True)
        
        cl = cleaning_instructions()
        ins = cl.instructions['NYC_SALES_CLEANING']

        orig_cols = list(ins.keys())
        df_new = df_sm.copy()[orig_cols]
        
        for column in orig_cols:
            if ins[column]['delete'] == 1:
                df_new = df_new.drop([column], axis=1)
            if ins[column]['delete'] == 0:
                df_new = df_new.rename(columns={column: ins[column]['new name']})
        
        df_new = df_new.reindex(df_new.columns.tolist(), axis=1) \
                       .astype(dtype={'SALE DATE': str})
        
        df_new['SALE DATE'] = pd.to_datetime(df_new['SALE DATE'])
        df_new = df_new.sort_values(by=['SALE DATE'], ascending=False) \
                       .reset_index(drop=True)
        
        return df_new

if __name__ == '__main__':
    cp = cleaning_pipeline()
    cp._extract_sales_data()