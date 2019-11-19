#!/usr/bin/env python

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'in progress'

### packages need to be imported 
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import os
import json

class trulia_dot_com:

    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._apt_urls_buy = []
        self._apt_urls_rent = []
        self._apt_urls_sold = []

    def _get_buy_webpage(self, pg_num, htype):
    
        overhead = 'https://www.trulia.com'
        dangle = 'for_sale'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()
        
        dict_alias = {
            'house': 'SINGLE-FAMILY_HOME',
            'condo': 'APARTMENT,CONDO,COOP',
            'townhouse': 'TOWNHOUSE',
            'multi-family': 'MULTI-FAMILY',
            'land': 'LOT%7CLAND',
            'mobile/manufactured': 'MOBILE%7CMANUFACTURED',
            'other': 'UNKNOWN',
        }
        
        aliases = [dict_alias[h] for h in htype]
        houses = ','.join(aliases)
        
        webpage = f'{overhead}/{dangle}/{city},{state}/{houses}_type/{pg_num}_p/'
        return webpage

    def _get_soup(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
        return soup

    def _get_buy_apt_urls_per_page(self,
                                   pg_num,
                                   htype=['house', 
                                          'multi-family']):

        webpage = self._get_buy_webpage(pg_num, htype)
        
        # Here we added User-Agent to the header of our request 
        # It is because sometimes the web server will check the
        # different fields of the header to block robot scrapers
        # User-Agent is the most common one because it is specific 
        # to your browser.
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(webpage, headers=headers)
        results = response.content

        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            
            apt_class = 'PropertyCard__PropertyCardContainer-sc-1ush98q-0 gsDQZj Box-sc-8ox7qa-0 jIGxjA'
            apt_tags = soup.find_all('div', class_=apt_class)
            
            apt_link_tags = [tag.find('a') for tag in apt_tags]
            apt_urls = [tag['href'] for tag in apt_link_tags]
        
        return apt_urls

    def _get_buy_apt_urls_ensemble(self,
                                   htype=['house', 
                                          'multi-family'],
                                   verbose=False,):
        stop = False
        urls_ensemble = ['']
        pg_num = 1
        while not stop:
            urls_per_pg = self._get_buy_apt_urls_per_page(pg_num, htype)
            
            if verbose:
                print(f'apartment URLs in page {pg_num} all done')
            
            if urls_per_pg == urls_ensemble[-1]:
                stop = True
            urls_ensemble.append(urls_per_pg)
            pg_num += 1
        
        def _flatten(lst):
            for el in lst:
                if isinstance(el, list):
                    yield from el
                else:
                    yield el
        
        urls_ensemble_cut = list(_flatten(urls_ensemble[1:-2]))
        if verbose:
            print('last 2 pages removed since they are the same.')
        return urls_ensemble_cut


if __name__ == '__main__':

    tdc = trulia_dot_com('philadelphia', 'pa')
    urls_all = tdc._get_buy_apt_urls_ensemble(verbose=True)
    print(len(urls_all))


