#!/usr/bin/env python

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'in progress'

import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import time
from fake_useragent import UserAgent
import os

### a class that contains all the contants we will be using 

class CONST:
    HEADER = 'https://www.elliman.com'

class elliman_dot_com:

    ############################
    # class initiation section #
    ############################

    def __init__(self):
        self._apt_urls = []
        self._apt_data = []

    #############################
    # private functions section #
    #############################

    def _random_user_agent(self):
        try:
            ua = UserAgent()
            return ua.random
        except:
            default_ua = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                    AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/58.0.3029.110 Safari/537.36'
            return default_ua

    def _get_soup(self, url):
    
        headers = {'User-Agent': self._random_user_agent()}
        
        response = requests.get(url, headers=headers)
        results = response.content
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
        return soup

    def _get_webpage(self, pg_num):
        template = f'https://www.elliman.com/search/for-sale/search-{pg_num}?sdid=1&sid=44458208&sk=1'
        return template 

    def _get_apt_urls_per_page(self, soup):
        apartments = soup.find_all('li', class_='listing_address first')
        apt_urls = [apt.find('a')['href'] for apt in apartments]
        apt_urls = [f'{CONST.HEADER}{url}' for url in apt_urls]
        return apt_urls

    def _get_apt_urls_ensemble(self, 
                               verbose=False, 
                               test=False):
        pg_num = 1
        stop = False
        apt_urls = []
        
        while not stop:
        
            if test and pg_num == 10:
                break
            
            if pg_num%50 == 0:
                if verbose:
                    print('50 pages scraped, sleep 15 seconds')
                time.sleep(15)
                
            webpage = self._get_webpage(pg_num)
            soup_pg = self._get_soup(webpage)
            apt_urls_pg = self._get_apt_urls_per_page(soup_pg)
            more_listings = soup_pg.find('div', class_='_grid33 _alpha')
            if (not apt_urls_pg) and (not more_listings):
                attempts = 1
                while attempts < 5:
                    time.sleep(3)
                    soup_pg = self._get_soup(webpage)
                    apt_urls_pg = self._get_apt_urls_per_page(soup_pg)
                    more_listings = soup_pg.find('div', class_='_grid33 _alpha')
                    
                    if apt_urls_pg or more_listings:
                        apt_urls += apt_urls_pg
                        if verbose:
                            print(f'apartment URLs in page {pg_num} all scraped')
                        pg_num += 1
                        continue
                    
                    attempts += 1
                        
                stop = True
            else:
                apt_urls += apt_urls_pg
                if verbose:
                    print(f'apartment URLs in page {pg_num} all scraped')
                pg_num += 1
        
        return apt_urls
    
    def _get_img_urls_per_apt(self, apt_url):
        soup_apt = self._get_soup(apt_url)
        photo_link = soup_apt.find('li', class_='listing_all_photos')\
                             .find('a')['href']
        photo_link = f'{CONST.HEADER}{photo_link}'
        soup_photo = self._get_soup(photo_link)

        imgs = soup_photo.find('div', class_='w_listitem_left')\
                         .find_all('img')
        imgs = [f"{CONST.HEADER}{img['src']}" for img in imgs]
        return imgs

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):
        try:
            current_path = os.getcwd()
            os.chdir(data_path)
            if not os.path.exists('Sale'):
                os.mkdir('Sale')
            os.chdir('Sale')
            
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

    def _get_address(self, soup):
        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            address = ppt_details.find('li', class_='first listing_address')\
                                 .get_text()

            addr_pattern = r'([A-Za-z0-9\s\-\,]+)? - ([A-Za-z0-9\s\-]+)?, ([A-Za-z0-9\s\-]+)?'
            street, neighborhood, city = re.findall(addr_pattern, address)[0]
            return street, neighborhood, city
        except:
            return None, None, None

    def _extract_num(self, text):
        """
        A helper function that extract any number from
        a text 

        Parameters
        ----------
        text : str
            a string of text that might contains numbers 

        Returns
        -------
        num : float
            the number extracted from the text 

        >>> _extract_num('$1000 per month')
        1000.0
        """
        try:
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan

    def _get_price(self, soup):
        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            price = ppt_details.find('li', class_='listing_price')\
                               .get_text()\
                               .replace(',','')
            return self._extract_num(price)
        except:
            return None

    def _get_features(self, soup):
        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            features = ppt_details.find('li', class_='listing_features')\
                                  .get_text()\
                                  .strip()\
                                  .split(' | ')

            beds, baths, halfbaths = 0, 0, 0
            for feature in features:
                if 'beds' in feature.lower():
                    beds = self._extract_num(feature)
                if 'baths' in feature.lower():
                    baths = self._extract_num(feature)
                if 'half bath' in feature.lower():
                    halfbaths = self._extract_num(feature)

            return beds, baths, halfbaths
        except:
            return None, None, None

    def _get_htype(self, soup):
        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            htype = ppt_details.find('li', class_='listing_extras')\
                               .get_text()\
                               .strip()
            return htype
        except:
            return None

    def _get_sqft(self, soup):
        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            all_props = ppt_details.find_all('li')
            props_text = [prop.get_text().strip() for prop in all_props]
            sqft = filter(lambda x: 'Approximate Sq. Feet' in x, props_text)
            sqft = list(sqft)[0].replace(',','')
            sqft = self._extract_num(sqft)
            return sqft
        except:
            return None

    def _get_list_id(self, soup):
        ppt_details = soup.find('div', class_='w_listitem_description')
        list_id = ppt_details.find('li', class_='listing_id')\
                             .get_text()\
                             .replace('Listing ID: ', '')\
                             .strip()
        return list_id

    def _get_apt_data(self, soup):
    
        street, neighborhood, city = self._get_address(soup)
        price = self._get_price(soup)
        beds, baths, halfbaths = self._get_features(soup)
        htype = self._get_htype(soup)
        sqft = self._get_sqft(soup)
        listid = self._get_list_id(soup)
        
        unit = [
            street, 
            neighborhood, 
            city,
            price,
            beds, 
            baths, 
            halfbaths,
            htype,
            sqft,
            listid,
        ]
        
        return unit

    ############################
    # public functions section #
    ############################

    def scrape_apt_urls(self, 
                        verbose=False, 
                        test=False):

        self._apt_urls = self._get_apt_urls_ensemble(verbose, test)

    def scrape_apt_data(self, 
                        apt_urls, 
                        verbose=False, 
                        test=False):
        apt_data = []

        if verbose:
            print(f'there are {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i == 10:
                break

            if verbose and i%10 == 0:
                print(f'{i} apartments have been scraped')

            soup = self._get_soup(url)
            unit = self._get_apt_data(soup)
            apt_data.append(unit)

        self._apt_data = apt_data

    def scrape_apt_images(self, 
                          apt_urls,  
                          data_path, 
                          verbose=False, 
                          test=False):

        if verbose:
            print(f'images in {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i==10:
                break

            if verbose and i%10==0:
                print('images in 10 apartments have been scraped')

            imgs = self._get_img_urls_per_apt(url)
            soup = self._get_soup(url)
            street, neighborhood, city = self._get_address(soup)

            self._save_images(imgs, data_path, street)

        if verbose:
            print('all images scraped')

    #####################
    # public attributes #
    #####################

    @property
    def apt_urls(self):
        return self._apt_urls

    @property
    def apt_data(self):
        return self._apt_data


if __name__ == '__main__':

    edc = elliman_dot_com()
    image_path = '../data/sample/elliman/imgdata'

    edc.scrape_apt_urls(verbose=True, test=True)
    apt_urls = edc.apt_urls
    edc.scrape_apt_data(apt_urls, verbose=True, test=True)
    edc.scrape_apt_images(apt_urls, image_path, verbose=True, test=True)

