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
        self._apt_urls = {
            'buy': [],
            'rent': [],
            'sold': [],
        }
        self._overhead = 'https://www.trulia.com'

    def _get_buy_webpage(self, pg_num, htype):
    
        overhead = self._overhead
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

    def _get_rent_webpage(self, pg_num):

        overhead = self._overhead
        dangle = 'for_rent'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()

        webpage = f'{overhead}/{dangle}/{city},{state}/{pg_num}_p/'
        return webpage

    def _get_sold_webpage(self, pg_num):

        overhead = self._overhead
        dangle = 'sold'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()

        webpage = f'{overhead}/{dangle}/{city},{state}/{pg_num}_p/'
        return webpage


    def _get_soup(self, url):

        # Here we added User-Agent to the header of our request 
        # It is because sometimes the web server will check the
        # different fields of the header to block robot scrapers
        # User-Agent is the most common one because it is specific 
        # to your browser.
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        results = response.content
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
        return soup

    def _get_apt_urls_per_page(self,
                               pg_num,
                               sales_type,
                               htype=['house', 
                                      'multi-family']):

        if sales_type.lower() == 'buy':
            webpage = self._get_buy_webpage(pg_num, htype)

        if sales_type.lower() == 'rent':
            webpage = self._get_rent_webpage(pg_num)

        if sales_type.lower() == 'sold':
            webpage = self._get_sold_webpage(pg_num)
        
        soup = self._get_soup(webpage)
        apt_class = 'PropertyCard__PropertyCardContainer-sc-1ush98q-0 gsDQZj Box-sc-8ox7qa-0 jIGxjA'
        apt_tags = soup.find_all('div', class_=apt_class)
        
        apt_link_tags = [tag.find('a') for tag in apt_tags]
        apt_urls = [f"{self._overhead}{tag['href']}" for tag in apt_link_tags]
        
        return apt_urls

    def _get_apt_urls_ensemble(self,
                               sales_type,
                               htype=['house', 
                                      'multi-family'],
                               verbose=False,
                               test=False):
        stop = False
        urls_ensemble = ['']
        pg_num = 1
        while not stop:
            urls_per_pg = self._get_apt_urls_per_page(pg_num, sales_type, htype)
            
            if verbose:
                print(f'apartment URLs in page {pg_num} all done')
            
            if urls_per_pg == urls_ensemble[-1]:
                stop = True
            urls_ensemble.append(urls_per_pg)
            pg_num += 1

            if test and pg_num == 5:
                break
        
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

    def _load_json(self, soup):
        jfile = soup.find('script', attrs={
            'id': '__NEXT_DATA__',
            'type': 'application/json',
        }).get_text()
        
        jdict = json.loads(jfile)
        return jdict

    def _get_img_urls(self, jdict):
        pics = jdict['props']['homeDetails']['media']['photos']
        urls = [pic['url']['mediumSrc'] for pic in pics]
        return urls

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     img_type, 
                     address):
        try:
            current_path = os.getcwd()
            os.chdir(data_path)
            
            if not os.path.exists(img_type):
                os.mkdir(img_type)
            os.chdir(img_type)

            if not os.path.exists(address):
                os.mkdir(address)
            os.chdir(address)

            for i, img_url in enumerate(img_urls):
                img_data = requests.get(img_url).content
                with open(f'img{i}.jpg', 'wb') as handler:
                    handler.write(img_data)
                    
            os.chdir(current_path)
            return 1
        
        except:
            return 0

    def _get_address(self, jdict):
        try:
            loc_dict = jdict['props']['homeDetails']['location']
            state = loc_dict['stateCode']
            city = loc_dict['city']
            zipcode = loc_dict['zipCode']
            street = loc_dict['formattedLocation']
            try:
                neighborhood = loc_dict['neighborhoodName']
            except:
                neighborhood = None
            return street, city, state, zipcode, neighborhood
        except:
            return None, None, None, None, None

    def _get_price(self, jdict):
        try:
            price_dict = jdict['props']['homeDetails']['price']
            return float(price_dict['price'])
        except:
            return None

    def _get_bedrooms_bathrooms(self, jdict):
        try:
            pattern = r'[-+]?\d*\.\d+|\d+'
            bed_dict = jdict['props']['homeDetails']['bedrooms']
            bath_dict = jdict['props']['homeDetails']['bathrooms']
            bedrooms = re.findall(pattern, bed_dict['summaryBedrooms'])[0]
            bathrooms = re.findall(pattern, bath_dict['summaryBathrooms'])[0]
            return float(bedrooms), float(bathrooms)
        except:
            return np.nan, np.nan

    def _get_apt_features(self, jdict):
        try:
            fdict_list = jdict['props']['homeDetails']['features']['attributes']
            features = []
            for fdict in fdict_list:
                try:
                    value = fdict['formattedValue']
                    try:
                        key = fdict['formattedName']
                        features.append(f'{key}:{value}')
                    except:
                        features.append(value)
                except:
                    next
            return ' | '.join(features)
        except:
            return None

    def scrape_apt_urls(self, sales_type, verbose=False, test=False):
        
        sales_type = sales_type.lower()
        self._apt_urls[sales_type] = self._get_apt_urls_ensemble(sales_type, verbose, test)


if __name__ == '__main__':

    tdc = trulia_dot_com('philadelphia', 'pa')
    urls_all = tdc._get_apt_urls_ensemble('sold', verbose=True, test=True)

    for url in urls_all:
        soup = tdc._get_soup(url)
        jdict = tdc._load_json(soup)
        img_urls = tdc._get_img_urls(jdict)
        address = tdc._get_address(jdict)[0].upper()
        data_path = '../data/sample/trulia/imgdata'
        tdc._save_images(img_urls, data_path, 'sold', address)


