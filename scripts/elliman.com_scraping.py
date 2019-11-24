import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import time
from fake_useragent import UserAgent
import os

class CONST
    HEADER = 'https://www.elliman.com'

class elliman_dot_com:

    def __init__(self):
        self._apt_urls = []
        self._apt_data = []

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

    def _get_apt_urls_ensemble(self, verbose=False, test=False):
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
                    soup_pg = get_soup(webpage)
                    apt_urls_pg = get_apt_urls_per_page(soup_pg)
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
        soup_apt = get_soup(apt_url)
        photo_link = soup_apt.find('li', class_='listing_all_photos')\
                             .find('a')['href']
        photo_link = f'{CONST.HEADER}{photo_link}'
        soup_photo = get_soup(photo_link)

        imgs = soup_photo.find('div', class_='w_listitem_left')\
                         .find_all('img')
        imgs = [f"{CONST.HEADER}{img['src']}" for img in imgs]
        return imgs                                