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

    def _get_buy_apt_urls_per_page(self, 
                                   pg_num,
                                   htype=['house', 
                                          'multi-family']):

        webpage = self._get_buy_webpage(pg_num, htype)
        response = requests.get(webpage)
        results = response.content

        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            apt_tags = soup.find_all('div', class_='PropertyCard__PropertyCardContainer-sc-1ush98q-0 gsDQZj Box-sc-8ox7qa-0 jIGxjA')
            print(apt_tags)


if __name__ == '__main__':

    tdc = trulia_dot_com('philadelphia', 'pa')
    print(tdc._get_buy_apt_urls_per_page(1))


