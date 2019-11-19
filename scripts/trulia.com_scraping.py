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
import datetime

class trulia_dot_com:

    ############################
    # class initiation section #
    ############################

    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._apt_urls = {
            'buy': [],
            'rent': [],
            'sold': [],
        }
        self._apt_data = {
            'buy': [],
            'rent': [],
            'sold': [],
        }
        self._overhead = 'https://www.trulia.com'

    #############################
    # private functions section #
    #############################

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

    def _get_space(self, jdict): 
        try:
            space_dict = jdict['props']['homeDetails']['floorSpace']
            space_text = space_dict['formattedDimension'].replace(',','')
            space = self._extract_num(space_text)
            return space
        except:
            return np.nan

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

    def _get_buy_apt_data(self, 
                          apt_urls, 
                          verbose=False, 
                          test=False):

        apt_info_data = []

        for url in apt_urls:
            soup = self._get_soup(url)
            jdict = self._load_json(soup)
            street, city, state, zipcode, neighborhood = self._get_address(jdict)
            price = self._get_price(jdict)
            bedrooms, bathrooms = self._get_bedrooms_bathrooms(jdict)
            space = self._get_space(jdict)
            features = self._get_apt_features(jdict)

            apt_info_data.append([
                street, 
                city, 
                state, 
                zipcode, 
                neighborhood,
                price,
                bedrooms, 
                bathrooms,
                space,
                features,
            ])

        return apt_info_data

    def _get_section_data(self, section):
        apt_name = section['name']
                
        try:
            bedrooms_text = section['bedrooms']['fullValue']
            bathrooms_text = section['bathrooms']['fullValue']
            bedrooms = self._extract_num(bedrooms_text)
            bathrooms = self._extract_num(bathrooms_text)
        except:
            bedrooms, bathrooms = np.nan, np.nan

        try:
            space = float(section['floorSpace']['max'])
        except:
            space = np.nan

        try:
            price_text = section['priceRange']['formattedPrice']
            price_text = price_text.replace(',', '') \
                                   .replace('$', '')
            price = self._extract_num(price_text)
        except:
            price = np.nan
            
        section_data = [
            apt_name,
            bedrooms,
            bathrooms,
            space,
            price,
        ]
        
        return section_data

    def _extract_num(self, text):
        try:
            if 'studio' in text.lower():
                return 0.0
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan

    def _get_floorplans(self, jdict):
        floorplans_groups = jdict['props']['homeDetails']['floorPlans']['floorPlanGroups']
        address_data = list(self._get_address(jdict))
        rental_data = []
        
        for floorplans in floorplans_groups:
            plans = floorplans['plans']
            for section in plans:
                section_data = self._get_section_data(section)
                rental_data.append(address_data+section_data)
                units = section['units']
                for unit in units:
                    unit_data = self._get_section_data(unit)
                    rental_data.append(address_data+unit_data)
        return rental_data

    def _get_rent_apt_data(self, 
                           apt_urls, 
                           verbose=False, 
                           test=False):

        apt_info_data = []

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            soup = self._get_soup(apt_url)
            jdict = self._load_json(soup)
            floorplan_data = self._get_floorplans(jdict)
            apt_info_data += floorplan_data

            if test and i==5:
                break

        return apt_info_data

    def _first(self, 
               iterable, 
               condition=lambda x: True):
        """
        Returns the first item in the 'iterable' that
        satisfies the 'condition'.

        If the condition is not given, returns the first item of
        the iterable.

        Return None if no item satysfing the condition is found.

        >>> first((1,2,3), condition=lambda x: x%2 == 0)
        2
        >>> first(range(3, 100))
        3
        """
        try:
            return next(x for x in iterable if condition(x))
        except:
            return None

    def _get_historical_prices_dict(self, jdict):
        try:
            price_history = jdict['props']['homeDetails']['priceHistory']
            price_sold = self._first(price_history, 
                               condition=lambda x: x['event'].lower() == 'sold')
            price_listed = self._first(price_history,
                                condition=lambda x: x['event'].lower() == 'listed for sale')
            try:
                start, end = price_history.index(price_sold), price_history.index(price_listed)
                price_history = price_history[start:end]
                price_change = self._first(price_history,
                                    condition=lambda x: x['event'].lower() == 'price change')
                return price_sold, price_change, price_listed
            except:
                return price_sold, None, price_listed
        except:
            return None, None, None

    def _unzip_pdict(self, price_dict):
        try:
            price_text = price_dict['price']['formattedPrice'].replace('$', '')\
                                                              .replace(',', '')
            price = self._extract_num(price_text)
            date = price_dict['formattedDate']
            date_formatted = datetime.datetime\
                                     .strptime(date, '%m/%d/%Y')\
                                     .strftime('%Y-%m-%d')
            return date_formatted, price
        except:
            return None, None

    def _get_normal_sold_prices(self, jdict):
        price_dict = jdict['props']['homeDetails']['price']
        try:
            sales_price_text = price_dict['formattedPrice'].replace(',','')\
                                                           .replace('$', '')
            sales_price = self._extract_num(sales_price_text)
            sales_date = price_dict['formattedSoldDate']
            sales_date_formatted = datetime.datetime\
                                           .strptime(sales_date, '%b %d, %Y')\
                                           .strftime('%Y-%m-%d')
            try:
                asking_price_text = price_dict['listingPrice']['formattedPrice'].replace(',','')\
                                                                                .replace('$', '')
                if 'k' in asking_price_text.lower():
                    asking_price = self._extract_num(asking_price_text)*1e3
                elif 'm' in asking_price_text.lower():
                    asking_price = self._extract_num(asking_price_text)*1e6
                else:
                    asking_price = self._extract_num(asking_price_text)
                return sales_date_formatted, sales_price, asking_price
            except:
                return sales_date_formatted, sales_price, np.nan
        except:
            return None, None, None
    

    def _get_important_sold_prices(self, jdict):
       
        pdict_s, pdict_c, pdict_l = self._get_historical_prices_dict(jdict)
        date_s, price_s = self._unzip_pdict(pdict_s)
        date_c, price_c = self._unzip_pdict(pdict_c)
        date_l, price_l = self._unzip_pdict(pdict_l)
        
        return date_s, price_s, date_c, price_c, date_l, price_l

    def _get_sold_info(self, jdict):
        street, city, state, zipcode, neighborhood = self._get_address(jdict)
        bedrooms, bathrooms = self._get_bedrooms_bathrooms(jdict)
        space = self._get_space(jdict)
        features = self._get_apt_features(jdict)
        sales_date, sales_price, ask_price = self._get_normal_sold_prices(jdict)
        sold_date, sold_price, change_date, change_price, list_date, list_price = self._get_important_sold_prices(jdict)
        
        sold_info = [
            street, 
            city, 
            state, 
            zipcode, 
            neighborhood,
            bedrooms, 
            bathrooms,
            space,
            features,
            sales_date, 
            sales_price, 
            ask_price,
            sold_date, 
            sold_price, 
            change_date, 
            change_price, 
            list_date, 
            list_price,
        ]
        
        return sold_info

    def _get_sold_apt_data(self, 
                           apt_urls, 
                           verbose=False, 
                           test=False):

        apt_info_data = []

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            soup = self._get_soup(apt_url)
            jdict = self._load_json(soup)
            sold_data = self._get_sold_info(jdict)
            apt_info_data += sold_data

            if test and i==5:
                break

        return apt_info_data

    ############################
    # public functions section #
    ############################

    def scrape_apt_urls(self, 
                        sales_type,
                        htype=['house', 
                               'multi-family'],
                        verbose=False, 
                        test=False):
        
        sales_type = sales_type.lower()
        self._apt_urls[sales_type] = self._get_apt_urls_ensemble(sales_type, 
                                                                 htype, 
                                                                 verbose, 
                                                                 test)

    def scrape_apt_data(self, 
                        apt_urls, 
                        verbose=False, 
                        test=False):
        pass


    def scrape_apt_images(self, 
                          sales_type,
                          data_path,
                          verbose=False, 
                          test=False):

        apt_urls = self._apt_urls[sales_type]

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i == 5:
                break

            soup = self._get_soup(url)
            jdict = self._load_json(soup)
            img_urls = self._get_img_urls(jdict)
            address = self._get_address(jdict)[0].upper()
            self._save_images(img_urls, 
                              data_path, 
                              sales_type,
                              address)

            if verbose and i%10==0:
                print(f'images in {i} apartments have been scraped')


if __name__ == '__main__':

    tdc = trulia_dot_com('philadelphia', 'pa')
    tdc.scrape_apt_urls('sold', verbose=True, test=True)

    print(tdc._get_sold_apt_data(tdc._apt_urls['sold'][:3]))

    img_path = '../data/sample/trulia/imgdata'
    tdc.scrape_apt_images('sold', img_path, verbose=True, test=True)

