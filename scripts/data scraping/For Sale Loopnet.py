__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'completed'

### packages need to be imported 
import pandas as pd
from bs4 import BeautifulSoup
import requests
import time
import numpy as np
import json
import re
import os
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class loopnet_dot_com:

    def __init__(self, city, state):
        self._city = city.replace(' ', '-').lower()
        self._state = state
        self._url = f'https://www.loopnet.com/{self._city}_multifamily-properties-for-sale/'

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
            default_ua = 'Mozilla/5.0 (Macintosh; Intel Mac O21S X 10_12_3) \
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
        if not response.status_code == 254:
            soup = BeautifulSoup(results, 'lxml')
        return soup

    ### parse the number from any string that contains numerical values 
    def _parse_num(self, text):
        try:
            text = text.replace(',', '')
            # extract the numerical price value 
            pattern = r'[-+]?\d*\.\d+|\d+'
            number = re.findall(pattern, text)[0]
            # convert the price to float 
            number = float(number)
            return number
        except:
            return None

    def _is_portfolio(self, description):
        description = description.lower()
        if 'portfolio' in description:
            return True
        else:
            return False

    ### get all the urls to access the information of the apartments 
    def _get_apt_urls(self):
        soup = self._get_soup(self._url)
        max_pg = soup.find_all('a', class_='searchPagingBorderless')[-1].text
        max_pg = int(self._parse_num(max_pg))

        apt_urls = []

        for i in range(1, max_pg+1):
            spg = self._get_soup(f'{self._url}{i}/')
            url_tags = spg.find_all('div', class_='listingDescription')
            urls = ['https://www.loopnet.com'+tag.find('a')['href'] for tag in url_tags]
            descriptions = [tag.find('span', class_='listingTitle').text for tag in url_tags]
            portfolio = np.array([self._is_portfolio(description) for description in descriptions])
            urls = np.array(urls)
            urls = urls[~portfolio]
            apt_urls = np.concatenate((apt_urls, urls), axis=0)

        return apt_urls

    def _get_apt_data(self, apt_url):
        pass

    def _get_img_urls(self, soup):
        class_list = ['mosaic-tile photo-landscape lazy', 'mosaic-tile photo-portrait lazy']
        img_tags = soup.find_all('div', class_=class_list)
        img_urls = [tag['data-src'] for tag in img_tags]
        return img_urls

if __name__ == '__main__':
    ldc = loopnet_dot_com('new york', 'ny')
    soup = ldc._get_soup('https://www.loopnet.com/Listing/1443-Beach-Ave-Bronx-NY/15121466/')
    urls = ldc._get_apt_urls()
    print(len(urls))