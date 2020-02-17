__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'complete'

### package requirements
import numpy as np
import pandas as pd
import urllib as ulb
import re
import requests
import os
import time
import json
import random

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
from fake_useragent import UserAgent

### constant
class CONST:
    # for sale 
    ELLIMAN_HEADER = 'https://www.elliman.com'

    ELLIMAN_COLNAMES = (
        'ADDRESS', 
        'NEIGHBORHOOD', 
        'CITY',
        'ASKING PRICE',
        'BED', 
        'BATH', 
        'HALF BATH',
        'LISTING TYPE',
        'GSF',
        'LISTING ID',
        'LINK',
    )

    # for rent 
    RENT_COLNAMES = (
        'ADDRESS',
        'CITY',
        'STATE',
        'ZIP',
        'APT #',
        'RENT',
        'BED',
        'BATH',
        'UNIT SF',
        'LINK',
    )

    TRULIA_OVERHEAD = 'https://www.trulia.com'

    TRULIA_COLNAMES = {
        'buy': (
            'ADDRESS', 
            'CITY', 
            'STATE', 
            'ZIP', 
            'ASKING PRICE',
            'BED', 
            'BATH',
            'GSF',
            'AMENITIES',
            'LINK',
        ),
        'rent': (
            'ADDRESS', 
            'CITY', 
            'STATE', 
            'ZIP', 
            'APT #',
            'BED',
            'BATH',
            'UNIT SF',
            'RENT',
            'LINK',
        ),
        'sold': (
            'ADDRESS', 
            'CITY', 
            'STATE', 
            'ZIP', 
            'BED', 
            'BATH',
            'GSF',
            'AMENITIES',
            'SALE DATE', 
            'SALE PRICE', 
            'ASKING PRICE',
            'SOLD DATE', 
            'SOLD PRICE', 
            'CHANGE DATE', 
            'CHANGE PRICE', 
            'LISTING DATE', 
            'LISTING PRICE',
            'LINK',
        ),
    }

    # for sale 
    REMAX_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE', 
        'ZIP',
        'PRICE',
        'BED',
        'BATH',
        'FIREPLACE',
        'GSF',
        'PROPERTY TYPE',
        'YEAR BUILT',
        'LOT SIZE',
        'WATERFRONT',
        'AC',
        'TAX AMOUNT',
        'TAX YEAR',
        'LINK',
    )

    # for rent 
    COMPASS_COLNAMES = (
        'ADDRESS', 
        'APT #',
        'CITY',
        'STATE', 
        'ZIP', 
        'RENT', 
        'BEDS', 
        'BATH', 
        'SF', 
        'YEAR BUILT', 
        'PROPERTY TYPE',
        '# UNITS', 
        '# FLOORS',
        'CENTRAL AC', 
        'WASHER/DRIER',
        'LAST PRICE',
        'LINK',
    )

    # for sale 
    LOOPNET_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE',
        'CAP RATE',
        'PROPERTY TYPE',
        '# UNITS',
        'PRICE',
        '# FLOORS',
        'GSF',
        'LAND SF',
        'BUILDING CLASS',
        'YEAR BUILT',
        'AVERAGE OCCUPANCY',
        'LINK',
    )

### For Sale 
class elliman_dot_com:

    ############################
    # class initiation section #
    ############################

    def __init__(self, city, state):
        self._apt_urls = []
        self._apt_data = []
        self._city = city
        self._state = state

    #############################
    # private functions section #
    #############################

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

    def _soup_attempts(self, url, total_attempts=5):

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

    def _get_webpage(self, pg_num):

        """
        Get the initial webpage for the apartments. Each webpage would contain 
        about 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_webpage(pg_num)
        'https://www.elliman.com/search/for-sale/search-2?sdid=1&sid=44458208&sk=1'
        """

        template = f'https://www.elliman.com/search/for-sale/search-{pg_num}?sdid=1&sid=44458208&sk=1'
        return template 

    def _get_apt_urls_per_page(self, soup):
        """
        
        A helper function that helps the user to scrape all the apartment URLs
        in the original webpage

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for the specific apartment page 

        Returns
        -------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in particular
            section

        >>> _get_apt_urls_per_page(soup)
        ['https://wwww.elliman.com/new-york-city/310-east-84th-street-manhattan-pwqwjvr',
         'https://wwww.elliman.com/new-york-city/250-west-73rd-street-manhattan-effcvao',
         'https://wwww.elliman.com/new-york-city/448-west-25th-street-manhattan-rdwscgq',
         ..., ]

        """

        # identify the tag that contains apt URL
        apartments = soup.find_all('li', class_='listing_address first')
        apt_urls = [apt.find('a')['href'] for apt in apartments]
        # formulate a complete apartment URL
        apt_urls = [f'{CONST.ELLIMAN_HEADER}{url}' for url in apt_urls]
        return apt_urls

    def _get_apt_urls_ensemble(self, 
                               verbose=False, 
                               test=False):
        """
        
        This is a helper function that will collectively scrape the apartments in all 
        of the original webpages in which each page contains roughly 30 apartments. 
        The function utilizes defensive programming strategy to avoid getting blocked
        as a bot.

        Parameters
        ----------
        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        apt_urls : list(str)
            this is a complete list of URLs for all the apartments

        """

        pg_num = 1 # initial page number
        stop = False # a flag to indicate whether or not to stop 
        apt_urls = [] # a list that contains a complete set of URLs
        
        # keep going until reaching the last page 
        while not stop:
        
            if test and pg_num == 10:
                break
            
            if pg_num%50 == 0:
                # sleep 15 seconds for every batch 
                if verbose:
                    print('50 pages scraped, sleep 15 seconds')
                time.sleep(15)
                
            webpage = self._get_webpage(pg_num)
            soup_pg = self._soup_attempts(webpage)
            apt_urls_pg = self._get_apt_urls_per_page(soup_pg)
            more_listings = soup_pg.find('div', class_='_grid33 _alpha')

            # try to make sure we reach the last page 
            # condition 1 - if there're no more contents in regular page
            # condition 2 - subscriped contents also non-existent 
            if (not apt_urls_pg) and (not more_listings):
                attempts = 0
                while attempts < 5:
                    time.sleep(3)
                    # another 5 attempts to request a soup 
                    soup_pg = self._soup_attempts(webpage)
                    apt_urls_pg = self._get_apt_urls_per_page(soup_pg)
                    more_listings = soup_pg.find('div', class_='_grid33 _alpha')
                    
                    # if we finally get results
                    if apt_urls_pg or more_listings:
                        apt_urls += apt_urls_pg
                        if verbose:
                            print(f'apartment URLs in page {pg_num} all scraped')
                        pg_num += 1
                        break # break the loop 
                    attempts += 1
                
                if pg_num < 470:
                    # last check - we know the total number of pages is
                    # greater than 470        
                    stop = False
                else: 
                    # the last page has been reached 
                    stop = True
            else:
                # have not reached the end page yet, keep going 
                apt_urls += apt_urls_pg
                if verbose:
                    print(f'apartment URLs in page {pg_num} all scraped')
                pg_num += 1 # next page 
        
        return apt_urls
    
    def _get_img_urls_per_apt(self, apt_url):

        """
        Find the image URLs given the URL of an apartment

        Parameters
        ----------
        apt_url : str
            the URL of a specific apartment or a general website

        Returns
        -------
        imgs_complete : list(str)
            this is a list of image URLs that you are able to 
            directly download 

        >>> _get_img_urls_per_apt(apt_url)
        ['https://www.elliman.com/img/28ea62bf97218c78209c8f817602a278cd375825+440++1',
         'https://www.elliman.com/img/a1d89f0c403d17c150dec8e213eee8a1c71a67ee+440++1',
         'https://www.elliman.com/img/21be72cc0dc3df9f33739a88fdb025769b46b6a0+440++1',
         ..., ]
        """

        try:
            # multiple attempts until you get the desired soup for the apartment
            soup_apt = self._soup_attempts(apt_url)
            # scrape the gallery link
            photo_link = soup_apt.find('li', class_='listing_all_photos')\
                                 .find('a')['href']
            # construct the gallery URL
            photo_link = f'{CONST.ELLIMAN_HEADER}{photo_link}'
            # try to scrape the contents in the gallery URL
            soup_photo = self._soup_attempts(photo_link)
            # try to find a list of images and their corresponding URLs
            imgs = soup_photo.find('div', class_='w_listitem_left')\
                             .find_all('img')
            imgs_complete = []

            for img in imgs:
                # special image link with complete address
                if 'http' in img['src']:
                    imgs_complete.append(img['src'])
                else:
                    # this is the images that are available from the 
                    # website server 
                    imgs_complete.append(f"{CONST.ELLIMAN_HEADER}{img['src']}")
            return imgs_complete
        except:
            return None

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):

        """
        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # if address is invalid, discontinue the process
            if not address:
                return 0

            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)
            
            # create a folder for the apartment if it doesn't
            # exist inside the section folder
            addr = f'{address}, {self._city.title()}, {self._state.upper()}'
            if not os.path.exists(addr):
                os.mkdir(addr)
            os.chdir(addr)

            # write images inside the apartment folder
            for i, img_url in enumerate(img_urls):
                img_data = requests.get(img_url).content
                with open(f'img{i}.jpg', 'wb') as handler:
                    handler.write(img_data)
                    
            os.chdir(current_path)
            return 1
        except:
            os.chdir(current_path)
            return 0

    def _get_address(self, soup):

        """
        A helper function that gets the address info of the apartment given 
        the soup of the specific apartment you are scraping 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage       

        Returns
        -------
        tuple
            address information, namely, (street, neighborhood, city)

        >>> _get_address(soup)
        ('35 Sidney Pl', 'Brooklyn Heights', 'New York')
        """

        try:
            # property detail tag
            ppt_details = soup.find('div', class_='w_listitem_description')
            # find address tag
            address = ppt_details.find('li', class_='first listing_address')\
                                 .get_text()
            # pattern for the address in this website
            addr_pattern = r'([A-Za-z0-9\s\-\,]+)? - ([A-Za-z0-9\s\-]+)?, ([A-Za-z0-9\s\-]+)?'
            # scrape out the address information
            street, neighborhood, city = re.findall(addr_pattern, address)[0]
            return street, neighborhood, city
        except:
            return None, None, None

    def _extract_num(self, text):
        """
        A helper function that extract any number from a text 

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
            # pattern to find any number (int or float)
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan

    def _get_price(self, soup):

        """
        A helper function that gets the price info of the apartment given 
        the soup of the specific apartment you are scraping 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        float
            price of the apartment

        >>> _get_price(soup)
        650000.0

        """

        try:
            # property details tag
            ppt_details = soup.find('div', class_='w_listitem_description')
            # price tag
            price = ppt_details.find('li', class_='listing_price')\
                               .get_text()\
                               .replace(',','') # clean up the text
            return self._extract_num(price) # extract number from the text
        except:
            return None

    def _get_features(self, soup):

        """

        A helper function that gets the bedroom and bathroom info of the 
        apartment given the soup of the specific apartment you are scraping 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        tuple
            # of bedrooms, # of bathrooms and # of half bathrooms

        >>> _get_features(soup)
        (5.0, 3.0, 0.0)

        """

        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            features = ppt_details.find('li', class_='listing_features')\
                                  .get_text()\
                                  .strip()\
                                  .split(' | ')

            beds, baths, halfbaths = 0, 0, 0
            # try to identify the room type
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
        """
        A helper function that gets listing type of the apartment given the 
        soup of the specific apartment you are scraping 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        str
            the listing type

        >>> _get_htype(soup)
        'Multi-family'
        """
        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            # housing type tag
            htype = ppt_details.find('li', class_='listing_extras')\
                               .get_text()\
                               .strip()
            return htype
        except:
            return None

    def _get_sqft(self, soup):
        """

        A helper function that gets the square foot of the apartment given the 
        soup of the specific apartment you are scraping 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        float
            the area of the apartment in square foot 

        >>> _get_sqft(soup)
        3012.0

        """

        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            all_props = ppt_details.find_all('li')
            props_text = [prop.get_text().strip() for prop in all_props]
            # filter out the element that contains specific text 
            sqft = filter(lambda x: 'Approximate Sq. Feet' in x, props_text)
            sqft = list(sqft)[0].replace(',','')
            sqft = self._extract_num(sqft)
            return sqft
        except:
            return None

    def _get_list_id(self, soup):
        """

        A helper function that gets the listing ID of the apartment given the 
        soup of the specific apartment you are scraping. Please note that the
        result is a string instead of a number 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        str
            the listing ID of the specific apartment 

        >>> _get_list_id(soup)
        '4008777'

        """

        try:
            ppt_details = soup.find('div', class_='w_listitem_description')
            # find listing ID tag
            list_id = ppt_details.find('li', class_='listing_id')\
                                 .get_text()\
                                 .replace('Listing ID: ', '')\
                                 .strip()
            return list_id
        except:
            return None

    def _get_apt_data(self, url):

        """

        A function that collects all the data we will need for an apartment

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        unit : list
            a list that contains the apartment info data. All the relevant 
            features are specified with the previous functions      

        """
        soup = self._soup_attempts(url)
        street, neighborhood, city = self._get_address(soup)
        price = self._get_price(soup)
        beds, baths, halfbaths = self._get_features(soup)
        htype = self._get_htype(soup)
        sqft = self._get_sqft(soup)
        listid = self._get_list_id(soup)
        
        # create a list that package all the useful data
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
            url,
        ]
        
        return unit

    ############################
    # public functions section #
    ############################

    def scrape_apt_urls(self, 
                        verbose=False, 
                        test=False):

        """
        A public function that allows you to call to scrape apartment URLs

        Parameters
        ----------
        verbose : boolean
            a flag you can enable to see the scraping progress

        test : boolean
            a flag you can toggle in order to run a small sample to avoid
            runtime issues

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_urls will be updated
            and all the apartments URLs will be stored in this field 
        """

        self._apt_urls = self._get_apt_urls_ensemble(verbose, test)

    def scrape_apt_data(self, 
                        apt_urls, 
                        verbose=False, 
                        test=False):

        """
        A public function that allows you to scrape information for a list
        of apartments the users specified 

        Parameters
        ----------
        apt_urls : list(str)
            a list of apartment URLs that you hope to scrape the apartment 
            info from

        verbose : boolean
            a flag you can enable to see the scraping progress

        test : boolean
            a flag you can toggle in order to run a small sample to avoid
            runtime issues

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_data will be updated
            and all the apartments info will be stored in this field 
        """

        apt_data = []

        if verbose:
            print(f'data in {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i == 10:
                break
            try:
                # update apartment info to the list
                unit = self._get_apt_data(url)
                apt_data.append(unit)
            except:
                print(soup)
                raise ValueError(f'FAILED apt url: {url}')

        # automatically updating the private attribute _apt_data
        self._apt_data = apt_data

    def scrape_apt_images(self, 
                          apt_urls,  
                          data_path, 
                          verbose=False, 
                          test=False):

        """
        
        Based on a list of apartment URLs the users want to scrape their images from, 
        the scraper will automatically write the images onto the local machine. Please 
        note that if 'test' is opted out, the size of the images will become significant. 

        Parameters
        ----------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        data_path : str
            the string of the path to where you want to store the images 

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the images will be saved onto the local machine 

        """

        if verbose:
            print(f'images in {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i==10:
                break

            try:
                imgs = self._get_img_urls_per_apt(url)
                soup = self._soup_attempts(url)

                # if we don't get any response from the website server
                # continue to call a few times in order to fetch web
                # contents. Give up after 5 attempts 
                if (not imgs) or (not soup):
                    attempts = 0
                    while attempts < 5:
                        time.sleep(3)
                        imgs = self._get_img_urls_per_apt(url)
                        soup = self._soup_attempts(url)
                        attempts += 1
                        # if contents are recovered, good to go.
                        if imgs and soup:
                            break
                # street is the name of the image folder 
                street, _, _ = self._get_address(soup)
                # automatically save images onto the local machine 
                self._save_images(imgs, data_path, street)
            except:
                # time to give up and try to find what's going on
                raise ValueError(f'FAILED apt: {street}, url: {url}')

        if verbose:
            print('all images scraped')

    def write_data(self,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory
        # check if the data exists, if not, create a new data file
        if not os.path.exists('elliman_dot_com.csv'):
            df = pd.DataFrame([], columns=CONST.ELLIMAN_COLNAMES)
            df.to_csv('elliman_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.ELLIMAN_COLNAMES)
        with open('elliman_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path, test=False):
        # time of sleep 
        sleep_secs = 15

        # scrape all the apartment URLs
        # notice the test is opted out here
        self.scrape_apt_urls(verbose=True, test=test)
        apt_urls = self.apt_urls # fetch the apartment URLs

        # divide the apartment URLs list into small batches 
        url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

        # batch jobs start
        print(f'total number of batches: {len(url_batches)}')
        for i, batch in enumerate(url_batches):
            print(f'batch {i} starts, there are {len(batch)} apartment URLs')
            self.scrape_apt_data(batch, verbose=True, test=test)
            self.scrape_apt_images(batch, img_path, verbose=True, test=test)
            apt_data = self.apt_data
            self.write_data(apt_data, data_path)
            print(f'batch {i} done, sleep {sleep_secs} seconds\n')
            time.sleep(15) # rest for a few seconds after each batch job done
        print('job done, congratulations!')

    #####################
    # public attributes #
    #####################

    @property
    def apt_urls(self):
        """
        A public attribute that lets you get access to all
        of the apartment URLs that need to be scraped. Notice
        that this is essentially a dictionary
        """
        return self._apt_urls

    @property
    def apt_data(self):
        """
        A public attribute that lets you get access to all
        of the apartment data that need to be scraped.
        """
        return self._apt_data

### For Rent 
class rent_dot_com:

    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._overhead = 'https://www.rent.com'
        self._browser, _ = self._get_browser(self._overhead)
        self._apt_urls = []
        self._apt_data = []

    @staticmethod
    def _build_options():
        options = webdriver.ChromeOptions()
        options.accept_untrusted_certs = True
        options.assume_untrusted_cert_issuer = True

        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-impl-side-painting")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-seccomp-filter-sandbox")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-cast")
        options.add_argument("--disable-cast-streaming-hw-encoding")
        options.add_argument("--disable-cloud-import")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-ipv6")
        options.add_argument("--allow-http-screen-capture")
        options.add_argument("--start-maximized")
        options.add_argument('--lang=es')

        return options

    def _get_browser(self, webpage):
        """
        A helper function to get the selenium browser in order 
        to perform the scraping tasks 

        Parameters
        ----------
        chromedriver : str
            the path to the location of the chromedriver 

        Returns
        -------
        browser : webdriver.Chrome
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """
        options = self._build_options()
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

    def _get_page_url(self, page_num):
        """
        Get the page link with a specific page.
        
        Parameters
        ----------
        page_num : int
            page number of the apartments in a specific city

        Returns
        -------
        string 
            the link of the page, given the page number 

        >>> _get_page_url(1)
        'rent.com/pennsylvania/philadelphia/apartments_condos_houses_townhouses?page=1'

        """

        # for city comes with 2 words, replace the space with -
        # e.g. 'new york' -> 'new-york'
        city = self._city.lower().replace(' ', '-')
        state = self._state.lower().replace(' ', '-')
        page = f'{self._overhead}/{state}/{city}/apartments_condos_houses_townhouses?page={page_num}'
        return page

    def _get_apt_urls_per_page(self, pg_num):
        """
        Get all the apartment URLs listed in the same page (30 URLs per page)

        Parameters
        ----------
        pg_num : int
            page number of the apartments in a specific city

        Returns:
        apt_urls : list(str)
            a list of apartment URLs correspond to different apartments in 
            a same page 

        """

        # get the URL for the specific page given its page number 
        pg_url = self._get_page_url(pg_num)
        response = requests.get(pg_url)
        # scrape the HTML web content from rent.com
        results = response.content 
        # a list that contains all the apartment URLs
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            apts = soup.find_all('a', attrs={'data-tid': 'property-title'})
            apt_urls = [apt['href'] for apt in apts]

        return apt_urls

    def _get_apt_urls(self, test=False, verbose=False):
        """
        Get all the relevant apartment links in rent.com with a specified city

        Parameters
        ----------
        verbose : boolean (optional)
            since the scraping process takes quite a while, you have the option
            to monitor the progress by enabling the status updates 

        Returns
        -------
        apt_urls : list(str)
            a list of apartment URLs correspond to different apartments in 
            a same page

        """

        # access the first page and navigate through the page to check the total
        # number of apartments
        pg_url = self._get_page_url(1)
        response = requests.get(pg_url)
        results = response.content
        page_num = 0
        apt_urls = []
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            # this is a tag that displays the total number of apartments
            apts_num =  soup.find('span', 
                                   attrs={'data-tid':'pagination-total'})\
                            .get_text()
            # try to convert text into integer 
            apts_num = int(apts_num)
            # since every page contains 30 apartments, divide the total number of 
            # apartments by 30 will give you the total number of pages
            pages_num = int(np.ceil(apts_num/30))
            # if enabled, you will see status updates on the terminal
            if verbose:
                print(f'total number of apartments in {self._city}, {self._state} is {apts_num}')
                print(f'total number of pages to be scraped is {pages_num}')
        
        # after getting the total number of pages that need to be scraped,
        # we can leave the rest for the loop to handle 
        for pg_num in range(pages_num):
            apt_urls += self._get_apt_urls_per_page(pg_num)
            if verbose:
                print(f'page {pg_num} done')

            if test:
                break 
        
        # make sure that all the links are in the state user specified 
        apt_urls = [url for url in apt_urls if self._state in url]
        return apt_urls

    def _get_address(self, address_tag, hdr):
        """
        Scrape the address of the apartment given the address HTML tag

        Parameters
        ----------
        address_tag : bs4.element.Tag
            a beautifulsoup element tag containing address information
            of the apartment

        hdr : bs4.element.Tag
            a beautifulsoup element tag containing header information of
            the apartment in case there's no address in the address section
            of the webpage 

        Returns
        -------
        (address, city, state, zipcode) : tuple(str)

        >>> _get_address(address_tag, hdr)
        ('1015 S 18th St', 'Philadelphia', 'Pennsylvania', '19146')

        """

        # try to find all the span tags in the address tag, the span tags
        # include all the address information we need 
        try:
            elements = address_tag.find_all('span')

            # scrape the text out of the span tags and remove
            # all the whitespaces and punctuation marks
            address = elements[0].get_text()\
                                 .replace(',','')\
                                 .strip()
            city = elements[1].get_text().strip()
            state = elements[2].get_text().strip()
            zipcode = elements[3].get_text().strip()
            return address, city, state, zipcode
        # however, sometimes the address tag does not include the street
        # info, in this case, use the text in the header tag, which serves
        # as a replacement for the address 
        except:
            address = hdr.get_text()
            elements = address_tag.find_all('span')
            city = elements[0].get_text()\
                                 .replace(',','')\
                                 .strip()
            state = elements[1].get_text().strip()
            zipcode = elements[2].get_text().strip()
            return address, city, state, zipcode

    def _get_units(self, unit_tag):
        """
        Scrape the actual apartments' information in the table provided by 
        a specific address

        -------

        When you open up the apartment page, this should be the units with 
        grey backgroud, rather than the rows in bright white background

        Parameters
        ----------
        unit_tag : bs4.element.Tag
            a beautifulsoup element tag that contains information about 
            the apartment unit

        Returns
        -------
        unit : list(Object)
            a list that contains information about the apartment unit, 
            including unit number, price, # bedrooms, # bathrooms and
            area measured in square foot 

        >>> _get_units(unit_tag)
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', '0606', 1894.0, 0.0, 1.0, 469.0)

        """

        # a list that contains apartment unit's information
        unit = []
        # use a loop to list all the cells in a row 
        for cell in unit_tag.find_all('td'):
            if cell.attrs: # omit the cell with nothing in it 
                # look for the apartment #, however, this info is not
                # consistent across the entire webiste
                if cell['data-tid'] == 'pdpfloorplans-unit-displayText':
                    unit_num = cell.get_text()
                    unit.append(unit_num)
                # scrape the price of the unit
                if cell['data-tid'] == 'pdpfloorplans-unit-price':
                    try:
                        unit_price = cell.get_text().replace('$', '')
                        # try to convert the price to float 
                        unit.append(float(unit_price))
                    except:
                        # if there's no price for this unit
                        # append the list with a null value 
                        unit.append(np.nan)
                if cell['data-tid'] == 'pdpfloorplans-unit-bedbath':
                    try:
                        # try to extract the tags that include the number
                        # of bedrooms and bathrooms 
                        bedbath_tag = cell.find_all('span')
                        bed_tag, bath_tag = bedbath_tag[0], bedbath_tag[1]
                        # regular expression pattern for extracting any types
                        # of numbers, including integer and floating numbers 
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        bed = re.findall(pattern, bed_tag.get_text())
                        bath = re.findall(pattern, bath_tag.get_text())
                        bed_unit, bath_unit = 0, 0
                        if bed:
                            bed_unit = bed[0]
                        if bath:
                            bath_unit = bath[0]
                        unit.append(float(bed_unit))
                        unit.append(float(bath_unit))
                    except:
                        # if the convertion failed, append the list
                        # will two null values 
                        unit.append(np.nan)
                        unit.append(np.nan)
                if cell['data-tid'] == 'pdpfloorplans-unit-sqft':
                    # follow the same procedure as above, but this time
                    # scrape the square foot of the apartment unit
                    try:
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        sqft_unit = re.findall(pattern, cell.get_text())[0]
                        unit.append(float(sqft_unit))
                    except:
                        unit.append(np.nan)
        return unit

    def _get_floorplan(self, unit_tag):
        """
        Scrape the actual apartments' information in the table provided by 
        a specific address

        -------

        very similar to the code in _get_units(unit_tag) function, this functino
        aims to scrape the apartment unit's info in the white background if you
        open the webpage. It's usually a summary of a list of apartments. 

        Parameters
        ----------
        unit_tag : bs4.element.Tag
            a beautifulsoup element tag that contains information about 
            the apartment unit

        Returns
        -------
        unit : list(Object)
            a list that contains information about the apartment unit, 
            including unit number, price, # bedrooms, # bathrooms and
            area measured in square foot 

        >>> _get_units(unit_tag)
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', 'Studio-S4B', '0606', 1894.0, 0.0, 1.0, 469.0)

        """
        unit = []
        for cell in unit_tag.find_all('td'):
            if cell.attrs:
                # scrape the apartment number 
                if cell['data-tid'] == 'pdpfloorplan-displayText':
                    floorplan_num = cell.get_text()
                    unit.append(floorplan_num)
                # scrape the apartment price 
                if cell['data-tid'] == 'pdpfloorplan-price':
                    try:
                        # remove any punctuation marks and $ sign
                        fp_price = cell.get_text()\
                                       .replace('$','')\
                                       .replace(',','')
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        price = re.findall(pattern, fp_price)[0]
                        unit.append(float(price))
                    except:
                        unit.append(np.nan)
                # scrape the number of bedrooms and bathrooms 
                if cell['data-tid'] == 'pdpfloorplan-bedbaths':
                    try:
                        bedbath_tag = cell.find_all('span')
                        bed_tag, bath_tag = bedbath_tag[0], bedbath_tag[1]
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        bed = re.findall(pattern, bed_tag.get_text())
                        bath = re.findall(pattern, bath_tag.get_text())
                        bed_fp, bath_fp = 0, 0
                        if bed:
                            bed_fp = bed[0]
                        if bath:
                            bath_fp = bath[0]
                        unit.append(float(bed_fp))
                        unit.append(float(bath_fp))
                    except:
                        unit.append(np.nan)
                        unit.append(np.nan)
                # scrape the area of the apartment in square foot 
                if cell['data-tid'] == 'pdpfloorplan-sqft':
                    try:
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        sqft_fp = re.findall(pattern, cell.get_text())[0]
                        unit.append(float(sqft_fp))
                    except:
                        unit.append(np.nan)
        return unit

    def _get_img_urls(self, url):
        try:
            browser = self._browser
            browser.get(url)

            button_gallery = browser.find_element_by_xpath("//button[@data-tid='pdp-gallery-photos-icon']")
            button_gallery.click()

            photos = browser.find_elements_by_xpath("//img[@data-tid='gallery-modal-thumbnail']")
            img_urls = [photo.get_attribute('src') for photo in photos]
            return img_urls
        except:
            return []

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):

        """
        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # if address is invalid, discontinue the process
            if not address:
                return 0

            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)
            
            # create a folder for the apartment if it doesn't
            # exist inside the section folder
            if not os.path.exists(address):
                os.mkdir(address)
            os.chdir(address)

            # write images inside the apartment folder
            for i, img_url in enumerate(img_urls):
                with open(f'img{i}.jpg', 'wb') as handler:
                    img_data = request.urlopen(img_url).read()
                    handler.write(img_data)
                    handler.close()
                    
            os.chdir(current_path)
            return 1
        except:
            os.chdir(current_path)
            return 0

    def _get_apt_info(self, apt_url, img_path):
        """
        Given the apartment URL, scrape the apartment unit's information regardless
        of what type of tag it is

        -------
        
        Systematically run through the entire webpage of the apartments located in a 
        fixed address, and scrape all the relevant information that's out there in the page.
        That being said, studio apartments, 1bed, 2beds etc. 

        Parameters
        ----------
        apt_url : str
            a specific apartment URL that has a fixed physical address

        Returns
        -------
        apt_all : list(Object) 
            a list of apartment information

        >>> _get_apt_info(apt_url)
        [('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', 'Studio-S4B', 1894.0, 0.0, 1.0, 469.0),
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', '0903', 1894.0, 0.0, 1.0, 469.0),
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', '1003', 1894.0, 0.0, 1.0, 469.0),
        ....]
        """

        # get the complete url of the apartments in a specified address 
        complete_url = self._overhead+apt_url
        response = requests.get(complete_url)
        results = response.content
        # a list that contains all the apartment information
        apt_all = []
        
        if not response.status_code == 404:
            try:
                soup = BeautifulSoup(results, 'lxml')
                # address tag
                address_tag = soup.find('div', attrs={'data-tid': 'pdpKeyInfo_address'})
                # header tag
                hdr = soup.find('h1', attrs={'data-tid': 'property-title'})
                # scrape the address information
                # get a tuple
                addr = self._get_address(address_tag, hdr)
                # a list of room tags, this might need to be constantly updated
                room_tags = soup.find_all('div', '_21XBf')
            except:
                return apt_all

            for rt in room_tags:
                # for each room tag, identify what type of rows the room tag is
                # only two options: unit in grey background, floorplan in white
                # background 
                room_table = rt.find('table', attrs={'data-tid': 'pdpfloorplan-table'})
                room_tbody = room_table.find('tbody')
                floor_plan = room_tbody.find_all('tr')
                apartments = []
                for unit_tag in floor_plan:
                    # unit tag
                    if unit_tag['data-tid'] == 'pdpfloorplan-row':
                        apt = list(addr)+self._get_floorplan(unit_tag)+[complete_url]
                        apartments.append(apt)
                    # floorplan tag
                    if unit_tag['data-tid'] == 'pdpfloorplans-unit-row':
                        apt = list(addr)+self._get_units(unit_tag)+[complete_url]
                        apartments.append(apt)
                # update the list that contains all the apartments info
                apt_all += apartments

            img_urls = self._get_img_urls(complete_url)
            if img_urls:
                self._save_images(img_urls, img_path, f"{addr[0]}, {self._city.replace('-', ' ').title()}, {self._state.upper()}")
                            
        return apt_all

    def scrape_apt_urls(self, test=False, verbose=False):
        """
        A public function that allows you to call to scrape apartment URLs

        Parameters
        ----------
        verbose : boolean
            a flag you can enable to see the scraping progress

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_urls will be updated
            and all the apartments URLs will be stored in this field 
        """
        self._apt_urls = self._get_apt_urls(test=test, verbose=verbose)

    def scrape_apt_data(self, apt_urls, img_path, verbose=False):
        """
        A public function that allows you to call to scrape apartment information

        Parameters
        ----------
        apt_urls : list(str)
            a list of apartment URLs that you hope to scrape the apartment 
            info from

        verbose : boolean
            a flag you can enable to see the scraping progress

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_data will be updated
            and all the apartments info will be stored in this field 
        """

        apt_all_data = []

        if verbose:
            print(f'apartments in {len(apt_urls)} addresses to be scraped')

        # loop through all the apartment URLs and scrape all the apartments
        # information in each URL
        for i, apt_url in enumerate(apt_urls):
            apt_all_data += self._get_apt_info(apt_url, img_path)
            if verbose:
                print(f'apartments in address {i} all scraped')

        self._apt_data = apt_all_data

    def write_data(self,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory

        # check if the data exists, if not, create a new data file
        if not os.path.exists(f'rent_dot_com.csv'):
            df = pd.DataFrame([], columns=CONST.RENT_COLNAMES)
            df.to_csv(f'rent_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.RENT_COLNAMES)
        with open(f'rent_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path, test=False, verbose=False):
        self.scrape_apt_urls(test=test, verbose=verbose)
        urls = self.apt_urls
        # in order to avoid crashes and loses all your data
        # divide the list of URLs in batches and keep updating
        # the csv file once the batch job is finished
        urls_chunk = np.array_split(urls, int(len(urls)//10))

        # running the batch and keep saving the intermediary 
        # results from the data scraping jobs 
        # each batch contains 10 URLs, but this could be modified
        for i, batch_urls in enumerate(urls_chunk):
            # print(batch_urls)
            self.scrape_apt_data(batch_urls, img_path, verbose=verbose)
            data = self.apt_data
            self.write_data(data, data_path)
            print(f'batch {i} finished running')

        self._browser.close()
        print('job finished!')

    @property
    def apt_urls(self):
        # serve as a way to show the apt_urls
        return self._apt_urls

    @property
    def apt_data(self):
        # serve as a way to show the apt_data
        return self._apt_data

### For Sale, For Rent
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
        self._browser, _ = self._get_browser(CONST.TRULIA_OVERHEAD)

    #############################
    # private functions section #
    #############################

    @staticmethod
    def _build_options():
        options = webdriver.ChromeOptions()
        options.accept_untrusted_certs = True
        options.assume_untrusted_cert_issuer = True

        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-impl-side-painting")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-seccomp-filter-sandbox")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-cast")
        options.add_argument("--disable-cast-streaming-hw-encoding")
        options.add_argument("--disable-cloud-import")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-ipv6")
        options.add_argument("--allow-http-screen-capture")
        options.add_argument("--start-maximized")
        options.add_argument('--lang=es')

        return options

    def _recaptcha(self, browser):
        captcha_iframe = WebDriverWait(browser, 10).until(
        EC.presence_of_element_located(
                (
                    By.TAG_NAME, 'iframe'
                )
            )
        )

        ActionChains(browser).move_to_element(captcha_iframe).click().perform()

        # click im not robot
        captcha_box = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located(
                (
                    By.ID, 'g-recaptcha-response'
                )
            )
        )

        browser.execute_script("arguments[0].click()", captcha_box)
        time.sleep(120)

    def _get_browser(self, webpage):
        """
        A helper function to get the selenium browser in order 
        to perform the scraping tasks 

        Parameters
        ----------
        chromedriver : str
            the path to the location of the chromedriver 

        Returns
        -------
        browser : webdriver.Chrome
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """
        options = self._build_options()
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 

        return browser, wait

    def _get_buy_webpage(self, pg_num, htype):

        """
        Get the initial webpage for the buy section apartments. Each webpage
        would contain about 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        htype : list(str)
            abbreviation for house type. A list that contains the house types
            user will be considering 

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_buy_webpage(pg_num, htype)
        'https://www.trulia.com/for_sale/Philadelphia,PA/SINGLE-FAMILY_HOME,MULTI-FAMILY_type/1_p/'
        """
    
        overhead = CONST.TRULIA_OVERHEAD
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

        if pg_num == 1:
            webpage = f'{overhead}/{dangle}/{city},{state}/{houses}_type/'

        return webpage

    def _get_rent_webpage(self, pg_num):

        """
        Get the initial webpage for the rent section apartments. Each webpage
        would contain roughly 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        htype : list(str)
            abbreviation for house type. A list that contains the house types
            user will be considering 

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_rent_webpage(pg_num, htype)
        'https://www.trulia.com/for_rent/Philadelphia,PA/1_p/'
        """

        overhead = CONST.TRULIA_OVERHEAD
        dangle = 'for_rent'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()

        webpage = f'{overhead}/{dangle}/{city},{state}/{pg_num}_p/'

        if pg_num == 1:
            webpage = f'{overhead}/{dangle}/{city},{state}/'

        return webpage

    def _get_sold_webpage(self, pg_num):

        """
        Get the initial webpage for the sold section apartments. Each webpage
        would contain roughly 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        htype : list(str)
            abbreviation for house type. A list that contains the house types
            user will be considering 

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_sold_webpage(pg_num, htype)
        'https://www.trulia.com/sold/Philadelphia,PA/1_p/'
        """

        overhead = CONST.TRULIA_OVERHEAD
        dangle = 'sold'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()

        # formulate the webpage
        webpage = f'{overhead}/{dangle}/{city},{state}/{pg_num}_p/'

        if pg_num == 1:
            webpage = f'{overhead}/{dangle}/{city},{state}/'

        return webpage

    def _get_apt_urls_per_page(self,
                               pg_num,
                               sales_type,
                               htype=['house', 
                                      'multi-family']):

        """
        A helper function that helps the user to scrape all the apartment URLs
        in the original webpage

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape
        
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        htype : list(str) (optional)
            abbreviation for house type. A list that contains the house types
            user will be considering. This will only be activated if sales_type == 'buy'
            since we don't care about the house type for rent and sold sections

        Returns
        -------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in particular
            section

        >>> _get_apt_urls_per_page()
        ['https://www.trulia.com/p/pa/philadelphia/511-s-13th-st-philadelphia-pa-19147--2090090499',
         'https://www.trulia.com/p/pa/philadelphia/1311-foulkrod-st-philadelphia-pa-19124--2017208781',
         ...
         ]
        """

        if sales_type.lower() == 'buy':
            # only buy section cares about house type
            webpage = self._get_buy_webpage(pg_num, htype)

        if sales_type.lower() == 'rent':
            webpage = self._get_rent_webpage(pg_num)

        if sales_type.lower() == 'sold':
            webpage = self._get_sold_webpage(pg_num)

        browser = self._browser
        browser.get(webpage)
        time.sleep(3)
        try:
            robot_check = browser.find_element_by_xpath("//div[@class='content center']")
            if 'I am not a robot' in robot_check.text:
                self._recaptcha(browser)
        except:
            pass
        
        # main content tag, need to be constantly updated
        apt_class = 'PropertyCard__PropertyCardContainer-sc-1ush98q-2 gKJaNz Box-sc-8ox7qa-0 jIGxjA'
        apt_tags = browser.find_elements_by_xpath("//div[@class='PropertyCard__PropertyCardContainer-sc-1ush98q-2 gKJaNz Box-sc-8ox7qa-0 jIGxjA']")

        # scrape all the apartment URLs
        apt_link_tags = [tag.find_element_by_tag_name('a') for tag in apt_tags]
        apt_urls = [f"{tag.get_attribute('href')}" for tag in apt_link_tags]
        return apt_urls

    def _get_apt_urls_ensemble(self,
                               sales_type,
                               htype=['house', 
                                      'multi-family'],
                               verbose=False,
                               test=False):

        """
        
        This is a helper function that will collectively scrape the apartments in 
        all of the original webpages in which each page contains roughly 30 apartments

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'
        
        htype : list(str) (optional)
            abbreviation for house type. A list that contains the house types
            user will be considering. This will only be activated if sales_type == 'buy'
            since we don't care about the house type for rent and sold sections
        
        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        urls_ensemble_cut : list(str)
            this is a list of URLs for all the apartments that we will ever care 
            in a section

        """

        stop = False # flag to tell the loop when to stop 
        urls_ensemble = [''] # a list that contains all the URLs
        pg_num = 1
        while not stop:
            # URLs per page are scraped
            urls_per_pg = self._get_apt_urls_per_page(pg_num, sales_type, htype)
            
            if verbose:
                print(f'apartment URLs in page {pg_num} all done')
            
            # if two consecutive lists of URLs are the same, we know 
            # the end of the loop has been reached
            if urls_per_pg == urls_ensemble[-1]:
                stop = True
            urls_ensemble.append(urls_per_pg)
            pg_num += 1

            if test and pg_num == 5:
                break
        
        # flatten a 2-D list
        def _flatten(lst):
            for el in lst:
                if isinstance(el, list):
                    yield from el
                else:
                    yield el
        
        # get rid of the redundant lists
        urls_ensemble_cut = list(_flatten(urls_ensemble[1:-2]))
        if verbose:
            print('last 2 pages removed since they are the same.')
        return urls_ensemble_cut

    def _load_json(self, url):

        """
        
        A helper function that find the JSON file inside the HTML file
        This is an Easter Egg indeed 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        jdict : dict
            a JSON object, a dictionary of dictionaries  

        """
        browser = self._browser
        browser.get(url)

        try:
            robot_check = browser.find_element_by_xpath("//div[@class='content center']")
            if 'I am not a robot' in robot_check.text:
                self._recaptcha(browser)
        except:
            pass

        jtext = browser.find_element_by_xpath("//script[@id='__NEXT_DATA__']")\
                       .get_attribute("innerHTML")
        
        # convert text to JSON
        jdict = json.loads(jtext) 
        return jdict

    def _get_img_urls(self, jdict):
        """
        Find the image URLs given the JSON file of an apartment

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        urls : list(str)
            this is a list of image URLs that you directly download 

        >>> _get_img_urls(jdict)
        ['https://static.trulia-cdn.com/pictures/thumbs_6/zillowstatic/ISvgw4ch9cdv430000000000.jpg',
         'https://static.trulia-cdn.com/pictures/thumbs_6/zillowstatic/IS7mojyi16a54a1000000000.jpg',
         ...
         ]
        """

        # find photos inside the JSON file
        pics = jdict['props']['homeDetails']['media']['photos']
        urls = [pic['url']['mediumSrc'] for pic in pics]
        return urls

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):

        """

        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        img_type : str
            the section of the webpage, namely, 'buy', 'rent' or 'sold'

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)

            # create a folder for the apartment if it doesn't
            # exist inside the section folder 
            addr = f'{address}, {self._city.title()}, {self._state.upper()}'
            if not os.path.exists(addr):
                os.mkdir(addr)
            os.chdir(addr)

            # write images inside the apartment folder 
            for i, img_url in enumerate(img_urls):
                img_data = requests.get(img_url).content
                with open(f'img{i}.jpg', 'wb') as handler:
                    handler.write(img_data)
            
            # go back to the original path before the 
            # function was initiated 
            os.chdir(current_path)
            return 1
        
        except:
            return 0

    def _get_address(self, jdict):
        
        """

        A helper function that gets the address info of the apartment given 
        the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        tuple
            address information

        >>> _get_address(jdict)
        ('302 Carpenter Ln', 'Philadelphia', 'PA', '19119', 'Mount Airy West')

        """
        
        try:
            # access the location info dictionary
            loc_dict = jdict['props']['homeDetails']['location']
            state = loc_dict['stateCode']
            city = loc_dict['city']
            zipcode = loc_dict['zipCode']
            street = loc_dict['formattedLocation']
            return street, city, state, zipcode
        except:
            return None, None, None, None

    def _get_price(self, jdict):

        """

        A helper function that gets the price info of the apartment given 
        the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        float
            price of the apartment

        >>> _get_price(jdict)
        650000.0

        """

        try:
            price_dict = jdict['props']['homeDetails']['price']
            return float(price_dict['price'])
        except:
            return None

    def _get_bedrooms_bathrooms(self, jdict):

        """

        A helper function that gets the bedroom and bathroom info of the 
        apartment given the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        tuple
            # of bedrooms and # of bathrooms

        >>> _get_bedrooms_bathrooms(jdict)
        (5.0, 3.0)

        """

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

        """

        A helper function that gets the square foot of the apartment given 
        the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        float
            the area of the apartment in square foot 

        >>> _get_space(jdict)
        3012.0

        """

        try:
            space_dict = jdict['props']['homeDetails']['floorSpace']
            space_text = space_dict['formattedDimension'].replace(',','')
            space = self._extract_num(space_text)
            return space
        except:
            return np.nan

    def _get_apt_features(self, jdict):

        """

        A helper function that gets the extra features of the apartment 
        given the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        str
            we stick all the extra features in a string separted by '|'
            since each apartment has its unique bonus features, it would 
            be infeasible to make them into columns

        >>> _get_apt_features(jdict)
        'Townhouse | $29/sqft | Lot Size:1,035 sqft | Built in 1940 | 6 Rooms | \
        Rooms:Dining Room | Heating:Forced Air | Heating Fuel:Gas | Cooling System:Central | \
        Air Conditioning | Great Views | Colonial Architecture | Stories:2 | Exterior:Brick | \
        Disabled Access'
        
        """

        try:
            fdict_list = jdict['props']['homeDetails']['features']['attributes']
            features = []
            for fdict in fdict_list:
                # find the extra features 
                try:
                    value = fdict['formattedValue']
                    try:
                        key = fdict['formattedName']
                        features.append(f'{key}:{value}')
                    except:
                        features.append(value)
                except:
                    next
            # stick all the features together, seperated by |
            return ' | '.join(features)
        except:
            return None

    def _get_buy_apt_data(self, 
                          apt_urls, 
                          verbose=False, 
                          test=False):

        """

        A function that collects all the data we will need for an apartment in 
        the buy category

        Parameters
        ----------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        apt_info_data : list
            all the relevant apartment information data        

        """

        apt_info_data = []

        for url in apt_urls:
            jdict = self._load_json(url)
            street, city, state, zipcode = self._get_address(jdict)
            price = self._get_price(jdict)
            bedrooms, bathrooms = self._get_bedrooms_bathrooms(jdict)
            space = self._get_space(jdict)
            features = self._get_apt_features(jdict)

            apt_info_data.append([
                street, 
                city, 
                state, 
                zipcode, 
                price,
                bedrooms, 
                bathrooms,
                space,
                features,
                url,
            ])

        return apt_info_data

    def _get_section_data(self, section):
        
        """

        A helper function to scrape rent apartment data based on the 
        section dictionary 

        Parameters
        ----------
        section : dict
            A dictionary that contains the floor plan information

        Returns
        -------
        section_data : list
            the apartment unit data

        >>> _get_section_data(section)
        ['2 Bed/2 Bath-B9', 2.0, 2.0, 1155.0, nan]
        """
        
        # unit number
        apt_name = section['name']
                
        try:
            # get the number of bedrooms and bathrooms based 
            # on the specific section dictionary
            bedrooms_text = section['bedrooms']['fullValue']
            bathrooms_text = section['bathrooms']['fullValue']
            bedrooms = self._extract_num(bedrooms_text)
            bathrooms = self._extract_num(bathrooms_text)
        except:
            bedrooms, bathrooms = np.nan, np.nan

        try:
            # get the square foot area of the unit 
            space = float(section['floorSpace']['max'])
        except:
            space = np.nan

        try:
            # get the rent price of the unit 
            price_text = section['priceRange']['formattedPrice']
            price_text = price_text.replace(',', '') \
                                   .replace('$', '')
            price = self._extract_num(price_text)
        except:
            price = np.nan
            
        # construct the section data
        section_data = [
            apt_name,
            bedrooms,
            bathrooms,
            space,
            price,
        ]
        
        return section_data

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
            if 'studio' in text.lower():
                return 0.0
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan

    def _get_floorplans(self, url):
        
        """
        This is a helper function that extract the floorplan information of 
        the rental apartments. The structure is very similar to rent.com

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries 

        Returns
        -------
        rental_data : list
            rental data, similar to rent.com
        """
        
        try:
            jdict = self._load_json(url)
            floorplans_groups = jdict['props']['homeDetails']['floorPlans']['floorPlanGroups']
            address_data = list(self._get_address(jdict))
            rental_data = []
            
            # different floorplans, e.g. studio, 1 bedroom 1 bathroom etc.
            for floorplans in floorplans_groups:
                plans = floorplans['plans']
                for section in plans:
                    # this is the header 
                    section_data = self._get_section_data(section)
                    rental_data.append(address_data+section_data+[url])
                    units = section['units']
                    # these are all the units under that header 
                    for unit in units:
                        unit_data = self._get_section_data(unit)
                        rental_data.append(address_data+unit_data+[url])
            return rental_data
        except:
            return None

    def _get_rent_apt_data(self, 
                           apt_urls, 
                           verbose=False, 
                           test=False):

        """
        This is a helper function that packages all the helper function regarding
        rental information extraction together 
        """

        apt_info_data = []

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            try:
                floorplan_data = self._get_floorplans(apt_url)
                if floorplan_data:
                    apt_info_data += floorplan_data

                if test and i==5:
                    break
            except:
                continue

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
        """
        find the historical price dictionary 
        """
        try:
            price_history = jdict['props']['homeDetails']['priceHistory']
            price_sold = self._first(price_history, 
                               condition=lambda x: x['event'].lower()=='sold')
            price_listed = self._first(price_history,
                                condition=lambda x: x['event'].lower()=='listed for sale')
            try:
                start, end = price_history.index(price_sold), price_history.index(price_listed)
                price_history = price_history[start:end]
                price_change = self._first(price_history,
                                    condition=lambda x: x['event'].lower()=='price change')
                return price_sold, price_change, price_listed
            except:
                return price_sold, None, price_listed
        except:
            return None, None, None

    def _unzip_pdict(self, price_dict):
        """
        helper function to unzip the price dictionary in the json file 
        """
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
        """
        get the normal price information, for example, sales price and asking price
        """
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
        """
        Get all the historical price information
        latest price sold, price change, and price listed 
        along with the corresponding dates 
        """
        pdict_s, pdict_c, pdict_l = self._get_historical_prices_dict(jdict)
        date_s, price_s = self._unzip_pdict(pdict_s)
        date_c, price_c = self._unzip_pdict(pdict_c)
        date_l, price_l = self._unzip_pdict(pdict_l)
        
        return date_s, price_s, date_c, price_c, date_l, price_l

    def _get_sold_info(self, url):
        """
        A helper function that packages all the sold apartment information
        """
        jdict = self._load_json(url)
        street, city, state, zipcode = self._get_address(jdict)
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
            url,
        ]
        
        return sold_info

    def _get_sold_apt_data(self, 
                           apt_urls, 
                           verbose=False, 
                           test=False):

        """
        
        This is a helper function that helps you obtain all the 
        sold apartments information. Please note that the information
        we need about the apartments differ when we have different types 
        of apartments. 

        Parameters
        ----------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        apt_info_data : list
            a list that contains all the information regarding the sold apartments 

        >>> _get_sold_apt_data(apt_urls)
        [['4419 Wayne Ave',
         'Philadelphia',
         'PA',
         '19140',
         'Logan',
         3.0,
         1.0,
         1188.0,
         'Townhouse | $29/sqft | Lot Size:1,035 sqft | Built in 1940 | 6 Rooms \
                | Rooms:Dining Room | Heating:Forced Air | Heating Fuel:Gas | \
                Cooling System:Central | Air Conditioning | Great Views | \
                Colonial Architecture | Stories:2 | Exterior:Brick | Disabled Access',
         '2019-11-15',
         35000.0,
         36000.0,
         '2019-11-15',
         35000.0,
         '2019-10-26',
         36000.0,
         '2019-10-10',
         45000.0], .... ]

        """

        apt_info_data = []

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            sold_data = self._get_sold_info(apt_url)
            apt_info_data.append(sold_data)

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

        """
        
        The main function you can use to scarpe the apartment URLs, the users only
        need to specify what sales_type the apartment is 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        htype : list(str) (optional)
            abbreviation for house type. A list that contains the house types
            user will be considering. This will only be activated if sales_type == 'buy'
            since we don't care about the house type for rent and sold sections

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the data will be saved in the private field of this class

        """
        
        sales_type = sales_type.lower()
        self._apt_urls[sales_type] = self._get_apt_urls_ensemble(sales_type, 
                                                                 htype, 
                                                                 verbose, 
                                                                 test)

    def scrape_apt_data(self, 
                        sales_type,
                        apt_urls,
                        verbose=False, 
                        test=False):

        """
        
        The main function you can use to scarpe the apartment data, the users only
        need to specify what sales_type the apartment is, as well as the apartment URLs

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the data will be saved in the private field of this class

        """

        # check which type of sales the user want to scrape 
        if sales_type == 'buy':
            self._apt_data['buy'] = self._get_buy_apt_data(apt_urls, verbose, test)
        if sales_type == 'rent':
            self._apt_data['rent'] = self._get_rent_apt_data(apt_urls, verbose, test)
        if sales_type == 'sold':
            self._apt_data['sold'] = self._get_sold_apt_data(apt_urls, verbose, test)


    def scrape_apt_images(self, 
                          sales_type,
                          apt_urls,
                          data_path,
                          verbose=False, 
                          test=False):

        """
        
        Based on the sales type, the scraper will automatically write the images onto 
        the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        data_path : str
            the string of the path to where you want to store the images 

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the images will be saved onto the local machine 

        """


        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i == 5:
                break

            jdict = self._load_json(url) # extract the json file
            img_urls = self._get_img_urls(jdict) # extract image URLs from the json file
            address = self._get_address(jdict)[0] # name of the folder 
            # write images onto the local machine 
            self._save_images(img_urls, 
                              data_path, 
                              address)

        if verbose:
            print(f'images in a total number of {len(apt_urls)} apartments have been scraped')

    def write_data(self,
                   sales_type,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory

        # check if the data exists, if not, create a new data file
        if not os.path.exists(f'trulia_dot_com_{sales_type}.csv'):
            df = pd.DataFrame([], columns=CONST.TRULIA_COLNAMES[sales_type])
            df.to_csv(f'trulia_dot_com_{sales_type}.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.TRULIA_COLNAMES[sales_type])
        with open(f'trulia_dot_com_{sales_type}.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path, test=False):
        # different sales categories 
        categories = ['rent', 'buy', 'sold']

        # scrape different streams of apartments iteratively 
        # could be optimized by parallel programming 
        for category in categories:
            print(f'scraping for category - {category} starts!')
            self.scrape_apt_urls(category, test=test, verbose=True)

        # divide the apartment URLs list into small batches 
        # in case the program crashes
        for category in categories:
            apt_urls = tdc.apt_urls[category]
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//20)

            # batch jobs start
            print(f'a total number of {len(url_batches)} batches, category={category}')
            for i, url_batch in enumerate(url_batches):
                try:
                    print(f'batch {i} starts')
                    self.scrape_apt_data(category, url_batch, verbose=True)
                    data = self.apt_data[category]

                    self.write_data(category, data, data_path)
                    self.scrape_apt_images(category, url_batch, img_path, verbose=True)
                except:
                    print(f'batch {i} failed')
                    print(f'unscraped URLs: {url_batch}')
                    continue

            print(f'scraping for category - {category} done!')

        self._browser.close()
        
        print('job done, congratulations!')

    #####################
    # public attributes #
    #####################

    @property
    def apt_urls(self):
        """
        A public attribute that lets you get access to all
        of the apartment URLs that need to be scraped. Notice
        that this is essentially a dictionary
        """
        return self._apt_urls

    @property
    def apt_data(self):
        """
        A public attribute that lets you get access to all
        of the apartment data that need to be scraped.
        """
        return self._apt_data

### For Sale
class remax_dot_com:

    # initialization - users need to specify a city and state 
    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._overhead = 'https://www.remax.com'
        self._apt_urls = []
        self._apt_data = []

    @staticmethod
    def _build_options():
        options = webdriver.ChromeOptions()
        options.accept_untrusted_certs = True
        options.assume_untrusted_cert_issuer = True
        
        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-impl-side-painting")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-seccomp-filter-sandbox")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-cast")
        options.add_argument("--disable-cast-streaming-hw-encoding")
        options.add_argument("--disable-cloud-import")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-ipv6")
        options.add_argument("--allow-http-screen-capture")
        options.add_argument("--start-maximized")
        options.add_argument('--lang=es')

        return options

    def _get_browser(self, webpage):
        """
        A helper function to get the selenium browser in order 
        to perform the scraping tasks 

        Parameters
        ----------
        chromedriver : str
            the path to the location of the chromedriver 

        Returns
        -------
        browser : webdriver.Chrome
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """
        options = self._build_options()
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

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

    def _soup_attempts(self, url, total_attempts=5):

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

    def _get_webpage(self):

        # for city comes with 2 words, replace the space with -
        # e.g. 'new york' -> 'new-york'
        city = self._city.strip().lower().replace(' ', '-')
        state = self._state.strip().lower().replace(' ', '-')
        # after the overhead, there's a dangle attached with the 
        # URL of this website 
        url = f'https://www.remax.com/homes-for-sale/{state}/{city}/city/4260000'
        return url

    def _get_ensemble_apt_urls(self, test=False):

        """
        Get all the relevant apartment links in remax.com with a specified city

        (private function)

        Parameters
        ----------
        verbose : boolean (optional)
            since the scraping process takes quite a while, you have the option
            to monitor the progress by enabling the status updates

        test : boolean (optional)
            this could be turned on for testing and debugging purposes. When it's
            turned on, only 50 pages' apartment URLs will be scraped so you have 
            faster runtime

        Returns
        -------
        apt_urls : list(str)
            a list of apartment URLs corresponding to different apartments in 
            a same page

        """

        webpage = self._get_webpage()
        browser, wait = self._get_browser(webpage)
        cookie = browser.find_element_by_xpath('//*[@id="__layout"]/div/div[3]/div/div[2]/button[1]')
        cookie.click()
        apt_urls = []

        try:
            while True:
                time.sleep(5)
                blocks = browser.find_elements_by_xpath("//div[@class='listings-card']//script[@type='application/ld+json']")
                for block in blocks:
                    jblock = json.loads(block.get_attribute('innerHTML'))
                    url = jblock[1]['url']
                    apt_urls.append(url)
                btn_next = wait.until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="__layout"]/div/div[2]/main/div/section[2]/div[2]/div/div[2]/div/button[last()]'))
                )
                btn_next.click()

                if test:
                    break
        except:
            pass

        return apt_urls

    def _parse_num(self, text):
        text = text.replace(',', '')
        # extract the numerical price value 
        pattern = r'[-+]?\d*\.\d+|\d+'
        number = re.findall(pattern, text)[0]
        # convert the price to float 
        number = float(number)
        return number

    def _get_price(self, soup):

        """
        Scrape the price of the apartment given the BeautifulSoup scraper 

        (private function)

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a BeautifulSoup scraper object that contains all the elements 
            in a webpage

        Returns
        -------
        price : float
            the price of the apartment (sell price, not rental price)

        >>> _get_price(soup)
        114000.0

        """

        try:
            # try to locate the price tag 
            price_tag = soup.find('div', class_='listing-detail-header-row md:ml-auto -ml-1')\
                            .find('h4', class_='h3')
            # remove punctuation marks 
            price_text = price_tag.get_text()\
                                  .replace(',','')\
                                  .strip()

            price = self._parse_num(price_text)
            return price
        except:
            return np.nan


    def _get_address(self, soup):

        """
        Scrape the address of the apartment given the content tag of 
        the specific apartment page 

        (private function)

        Parameters
        ----------
        content_tag : bs4.element.Tag
            a beautifulsoup element tag containing the content information
            of the apartment, including address, bedrooms, area etc. 

        Returns
        -------
        (street, city, state, zipcode) : tuple(str)

        >>> _get_address(content_tag)
        ('767 N 24TH ST', 'Philadelphia', 'PA', '19130')

        """

        try:
            # from the content tag, extract the tag that contains all the address info
            address_tag = soup.find('div', class_='flex flex-col md:flex-row')
            # street tag
            street_tag = address_tag.find('h1', class_='h3')
            # street information
            street = street_tag.get_text()\
                               .strip()\
                               .replace(',', '')
            # region tag      
            region_tag = address_tag.find('h5', class_='listing-card-location') \
                                    .get_text() \
                                    .strip() \
                                    .split(' ')
            # city information
            city = region_tag[0].replace(',', '').title()
            # state information
            state = region_tag[1]
            # zipcode information
            zipcode = region_tag[2]

            return street, city, state, zipcode
        
        except:
            # return None if any of the above parts failed
            # if there's any part that's missing in the address part,
            # the whole address becomes useless
            return None, None, None, None

    def _get_sideinfo(self, content_tag):

        """
        Scrape all the important information of the apartment given the 
        content tag of the specific apartment page 

        (private function)

        -------

        After inspection of the webpage, I find out that there are some 
        features some apartments have, but others don't have. Therefore,
        it would not be feasible if we want to store all the information 
        in a structured database. 

        Therefore, I tried my best to pick the common features almost 
        every apartment should have (list type, bathrooms, bedrooms ...) 
        and some unique and important features that might be missing 
        for a lot of other apartments 

        The best way to store all these unstructed information thus 
        comes to use a dictionary 

        Parameters
        ----------
        content_tag : bs4.element.Tag
            a beautifulsoup element tag containing the content information
            of the apartment, including address, bedrooms, area etc. 

        Returns
        -------
        sideinfo : dict
            a dictionary that contains all the information that an apartment 
            could have included in the webpage 

        >>> _get_sideinfo(content_tag)

        {'Listing Type': 'Condo/Townhome', 
        'Listing ID': 'PAPH848950', 
        'House Size': '2,159 sqft', 
        'Lot Size': '1,742.00 sqft'}

        """

        # dictionary that used to store all the relevant information
        # regarding an apartment
        sideinfo = {} 
        try:
            # main content of all the relavent features 
            apt_info_tags = content_tag.find_all('div', class_='flex flex-col pr-8')
            
            for apt_tag in apt_info_tags:
                # construct (key, value) pair for the dictionary 
                key = apt_tag.find('div', class_='data-name') \
                             .get_text() \
                             .strip()

                value = apt_tag.find('div', class_='data-value') \
                               .get_text() \
                               .strip()
                try:
                    value = self._parse_num(value)
                except:
                    pass

                # fill in the dictionary
                sideinfo[key] = value

            return sideinfo
        except:
            return sideinfo

    def _access_dict(self, d, key):
        """
        Access the dictionary with a known or unknown key without 
        breaking the program using defensive programming

        Parameters
        ----------
        d : dict
            a dictionary that contains all the features information
            of an apartment using _get_sideinfo() function

        key : str
            the key that the users want to extract the value from 
            the dictionary from  

        Returns
        -------
        value : str or float
            the function will try to identify any numerical value 
            and convert it to float. If it's supposed to be a string,
            it will leave it as it is 

        >>> _access_dict('Listing Type')
        'Condo/Townhome'

        >>> _access_dict('Lot Size')
        1742.00

        >>> _access_dict('Listing ID')
        'PAPH848950'

        """
        try:
            # try to get access to the value by using the key
            value = d[key]
            return value
        except:
            # fail to access the value from the key
            # namely, the feature does not exist in the 
            # feature dictionary of a specific apartment
            return None

    def _parse_year(self, year):
        try:
            return int(year)
        except:
            return year

    def _remax_apt(self, complete_url, img_path):

        """
        Scrape all the relavent information of the apartment given 
        the content tag of the specific apartment page and standardize
        them into a structured format 

        (private function)

        Parameters
        ----------
        content_tag : bs4.element.Tag
            a beautifulsoup element tag containing the content information
            of the apartment, including address, bedrooms, area etc. 

        Returns
        -------
        list(Object)
            list that contains features information about an apartment 

        >>> _remax_apt(soup, content_tag)
        ['767 N 24TH ST', 'Philadelphia', 'PA', '19130', ... , 'Philadelphia', None, 'Fairmount']

        """

        # as dicussed earlier, the best format to store all the information
        # is by creating dictionaries to store the unstructured information
        # but here are the features that are common across all aparments and 
        # I also picked some features I think are important
        soup = self._soup_attempts(complete_url)
        price = self._get_price(soup)
        street, city, state, zipcode = self._get_address(soup)
        sidict = self._get_sideinfo(soup)
        bedrooms = self._access_dict(sidict, 'Bedrooms Total')
        bathrooms = self._access_dict(sidict, 'Bathrooms Total')
        fireplace = self._access_dict(sidict, 'Fireplace')
        living_area = self._access_dict(sidict, 'Living Area')
        property_type = self._access_dict(sidict, 'Property Type')
        year_built = self._parse_year(self._access_dict(sidict, 'Year Built'))
        lot_size = self._access_dict(sidict, 'Lot Size')
        waterfront = self._access_dict(sidict, 'Waterfront')
        ac = self._access_dict(sidict, 'Air Conditioning')
        tax = self._access_dict(sidict, 'Tax Annual Amount')
        tax_year = self._parse_year(self._access_dict(sidict, 'Tax Year'))

        # package all the features into a list 
        unit = [
            street, 
            city, 
            state, 
            zipcode,
            price,
            bedrooms,
            bathrooms,
            fireplace,
            living_area,
            property_type,
            year_built,
            lot_size,
            waterfront,
            ac,
            tax,
            tax_year,
            complete_url,
        ]

        img_urls = self._get_img_urls(soup)
        if img_urls:
            self._save_images(img_urls, img_path, f"{street.title()}, {city.replace('-', ' ').title()}, {state.upper()}")

        return unit

    def _get_img_urls(self, soup):
        img_tags = soup.find_all('img', class_='listing-detail-image')
        img_urls = [tag['src'] for tag in img_tags]
        return img_urls

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):

        """
        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # if address is invalid, discontinue the process
            if not address:
                return 0

            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)
            
            # create a folder for the apartment if it doesn't
            # exist inside the section folder
            if not os.path.exists(address):
                os.mkdir(address)
            os.chdir(address)

            # write images inside the apartment folder
            for i, img_url in enumerate(img_urls):
                img_data = requests.get(img_url).content
                with open(f'img{i}.jpg', 'wb') as handler:
                    handler.write(img_data)
                    
            os.chdir(current_path)
            return 1
        except:
            os.chdir(current_path)
            return 0

    def _get_apt_info(self, apt_url, img_path):

        """
        Given the apartment URL, scrape the apartment unit's information regardless
        of what type of apartment it is. 

        (private function)

        -------
        
        In this website, we have two types of apartment, namely, normal apartments 
        and collection apartments. Normal apartments have a bright blue background 
        which forms the majority the apartments in this website. 

        Collection apartments are luxurious type apartments that have their own 
        specially designed webpages to differentiate from the normal apartment 
        webpages (dark navy background). We need to identify  these two different 
        types of apartments and handle them differently.   

        Parameters
        ----------
        apt_url : str
            a specific apartment URL that has a fixed physical address

        Returns
        -------
        apt_all : list(list(Object)) 
            a list of apartment information

        >>> _get_apt_info(apt_url)
        [['767 N 24TH ST', 'Philadelphia', 'PA', '19130', ... , 'Philadelphia', None, 'Fairmount', 'Yes'],
         ['1417 N 8TH ST', 'Philadelphia', 'PA', '19122', ... , 'Philadelphia County', None, 'Ludlow', 'Yes']
         ...]
        """
        complete_url = self._overhead+apt_url
        response = requests.get(complete_url)
        results = response.content
        
        if not response.status_code == 404:
            # append the luxury feature as an additional column
            apt_info = self._remax_apt(complete_url, img_path)

        return apt_info

    def scrape_apt_urls(self, test=False):

        """
        A public function that allows you to call to scrape apartment URLs

        (public function)

        Parameters
        ----------
        verbose : boolean (optional)
            a flag you can enable to see the scraping progress

        test : boolean (optional)
            a flag that allows you to test run your code 
            with small sample size 

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_urls will be updated
            and all the apartments URLs will be stored in this field 
        """

        self._apt_urls = self._get_ensemble_apt_urls(test=test)

    def scrape_apt_data(self, apt_urls, img_path, verbose=False):

        """
        A public function that allows you to call to scrape apartment information

        (public function)

        Parameters
        ----------
        apt_urls : list(str)
            a list of apartment URLs that you hope to scrape the apartment 
            info from

        verbose : boolean
            a flag you can enable to see the scraping progress

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_data will be updated
            and all the apartments info will be stored in this field 
        """

        apt_all_data = []

        if verbose:
            print(f'{len(apt_urls)} apartments to be scraped')

        # loop through all the apartment URLs and scrape all the apartments
        # information in each URL
        for i, apt_url in enumerate(apt_urls):
            apt_all_data.append(self._get_apt_info(apt_url, img_path)) 
        
        self._apt_data = apt_all_data

    def write_data(self,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory
        # check if the data exists, if not, create a new data file
        if not os.path.exists('remax_dot_com.csv'):
            df = pd.DataFrame([], columns=CONST.REMAX_COLNAMES)
            df.to_csv('remax_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.REMAX_COLNAMES)
        with open('remax_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path, test=False):
        # scrape all the apartment URLs in Philadelphia
        # status update enabled
        self.scrape_apt_urls(test=test)
        urls = self.apt_urls

        # in order to avoid crashes and loses all your data
        # divide the list of URLs in batches and keep updating
        # the csv file once the batch job is finished
        urls_chuck = np.array_split(urls, int(len(urls))//20)

        print(f'batch jobs started, {len(urls_chuck)} batches in total')

        # running the batch and keep saving the intermediary 
        # results from the data scraping jobs 
        # each batch contains 10 URLs, but this could be modified
        for i, batch_urls in enumerate(urls_chuck):
            self.scrape_apt_data(batch_urls, img_path, verbose=True)
            data = self.apt_data
            self.write_data(data, data_path)
            print(f'batch {i} finished running')

        print('job done!')

    @property
    def apt_urls(self):
        # public attritube 
        # serve as a way to show the apt_urls
        return self._apt_urls
    
    @property
    def apt_data(self):
        # public attribute 
        # serve as a way to show the apt_data
        return self._apt_data

### For Sale 
class coldwell_dot_com:

    def __init__(self, city, state, start_page, end_page):
        self._city = city.lower().replace(' ', '-')
        self._state = state.lower()
        self._start_page = start_page
        self._end_page = end_page

    def _get_link_content(self, url):
        ##Decorate the request with header and proxy
        my_headers=[
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
        ]

        headers = [
            ('Host', 'https://www.coldwellbankerhomes.com'), 
            ('Connection', 'keep-alive'), 
            ('Cache-Control', 'max-age=0'),
            ('User-Agent', random.choice(my_headers)),
        ]

        ##Please note the the size of proxy IPs may affect the performance,if the IP pools are small, may raise 403 Error (Server Forbidden)
        proxy_list = '138.197.222.35,36.89.65.253,105.19.59.192,109.110.73.106,176.9.75.42,200.89.178.63,138.68.161.14,188.226.141.61,139.59.109.156'.split(',')
        ##Add timer to sleep for 1 sec,in order to avoid getting blocked
        t = 1
        time.sleep(t)
        ##Decorate the url request with Header and Proxy IP
        proxy = random.choice(proxy_list)

        urlhandle = ulb.request.ProxyHandler({'http': proxy})
        opener = ulb.request.build_opener(urlhandle)
        opener.addheaders = headers
        ulb.request.install_opener(opener)
        response = ulb.request.Request(url)
        
        fp = ulb.request.urlopen(response)
        html = fp.read()
        fp.close
        content = BeautifulSoup(html,"lxml")
        return content
    
    def _get_content(self, url, img_path):
        
        listing_content = self._get_link_content(url)
        
        ## Scrap the address, city, state, zip_code, apt #, asking price
        address = listing_content.find('h1', class_='notranslate') \
                                 .find('span', class_='notranslate') \
                                 .get_text() \
                                 .strip() \
                                 .split(',')

        city = address[1].strip()
        state = address[2].strip().split(' ')[0].strip()
        zip_code = address[2].strip().split(' ')[1].strip()
        if len(address[0].split('#'))>1:
            street = address[0].split('#')[0].strip()
            apt_num = address[0].split('#')[1].strip()
        else:
            street = address[0].split('#')[0].strip()
            apt_num = 'N/A'
        asking_price = listing_content.find('span', itemprop='price').get_text()
        
        # Scrap the number of bedrooms,full bathroom, sqt, listing type
        title = str()
        for item in listing_content.find_all('ul', class_='details'):
            title += item.get_text().strip()
        try:
            listing_type = title.split('\n')[2]
            bedrooms = re.findall(r'[0-9]+ Bed\w?', title)[0].split(' ')[0]
            bathrooms = re.findall(r'[0-9]+ Full Bath\w?', title)[0].split(' ')[0]
            sqt = re.findall(r'[0-9]+ Sq. Ft', title)[0].split(' ')[0]
        except:
            bedrooms, bathrooms = 'N/A', 'N/A'
            try:
                sqt = re.findall(r'[0-9]+ Sq. Ft', title)[0].split(' ')[0]
            except:
                sqt = np.nan
            listing_type = title.split('\n')[2]

        ## Scrap all the other informations for this property
        details = str()
        for item in listing_content.find_all('li'):
            details+= item.get_text()+'\n'       
        for item in details.split('\n'):
            if re.findall(r'Construction:', item)!=[]:
                material = item.split(':')[1].strip()
                break
            else:
                material = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Lot Size', item):
                if item.split(':')[0] == 'Lot Size (Acres)':
                    lot_size = item.split(':')[1].strip()
                    break
            else:
                lot_size = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Basement:', item):
                base = item.split(':')[1].strip()
                break
            else:
                base = 'N/A'
        for item in details.split('\n'):      
            if re.findall(r'Basement Desc.:', item):
                base_desc = item.split(':')[1].strip()
                break
            else:
                base_desc = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Year Built:', item):
                year_built = item.split(':')[1].strip()
                break
            else:
                year_built = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Stories/Levels',item):
                floors = item.split(':')[1].strip()
                break
            else:
                floors = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Architectural Info',item):
                arch_info = item.split(':')[1].strip()
                break
            else:
                arch_info = 'N/A'
                
        listing_detail = {
            'ADDRESS': street,
            'CITY': city, 
            'STATE': state, 
            'ZIP': zip_code, 
            'APT #': apt_num, 
            'BATH': bathrooms,
            'BED': bedrooms, 
            'GSF': sqt,
            'ASKING PRICE': asking_price, 
            'LISTING TYPE': listing_type,
            'LOT SF': lot_size, 
            'YEAR BUILT': year_built, 
            'FLOORS': floors, 
            'BASEMENT': base,
            'BASEMENT DESC': base_desc, 
            'ARCH': arch_info, 
            'MATERIAL': material,
            'LINK': url,
        }

        ##Scrap all the image for each property and store them into each folder
        ##Please change the file_root accordingly when tested
        image_url = []
        for image_link in listing_content.find_all('img',class_="owl-lazy"):
            image_url.append(image_link.get('data-href'))

        file_root = img_path
        file_folder = ', '.join([street,city])
        file_path = os.path.join(file_root, file_folder)

        current_path = os.getcwd() 
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        os.chdir(file_path)

        for i in range(len(image_url)):
            f= open("{} {}.jpg".format(street,i+1),"wb")
            f.write(ulb.request.urlopen(image_url[i]).read())
            f.close

        os.chdir(current_path)
            
        return listing_detail

    def _get_df(self, content_list, save_to_excel=False):
        ## Store all the listing info to a dataframe, if choose to save as Excel Spread Sheet, pass True
        df = pd.DataFrame()
        for i in range(len(content_list)):
            temp_df = pd.DataFrame(content_list[i],index=[i])
            df = pd.concat([df,temp_df],axis=0, ignore_index=True)
        if not save_to_excel:
            df.to_excel("Phil_demo_data_2.xlsx")
        return df

    def _get_max_page(self):
        url = f'https://www.coldwellbankerhomes.com/{self._state}/{self._city}/?sortId=2&offset=0'
        content = self._get_link_content(url)
        pg_list = content.find('ul', class_='propertysearch-results-pager')
        pages = pg_list.find_all('li')
        max_pg = pages[-2].get_text()
        return int(max_pg)

    def scraping_pipeline(self, data_path, img_path, test=False):
        print(f'Coldwell Bankers For Sale - Start Scraping!')
        if self._end_page == 'max':
            self._end_page = self._get_max_page()

        ## Test the function and integrate the results
        url_list = ['https://www.coldwellbankerhomes.com/{}/{}?sortId=2&offset={}' \
                    .format(self._state, self._city, (i-1)*24) \
                    for i in range(self._start_page, self._end_page+1)]

        listing_link = []

        for url in url_list:
            content = self._get_link_content(url)
            for listing in content.find_all('div', class_="address notranslate"):
                listing_link.append('https://www.coldwellbankerhomes.com'+listing.find('a')['href'])

            if test:
                break

        content_list = []
        print(f'\ttotal number of aparments to be scraped: {len(listing_link)}')
        for i, url in enumerate(listing_link):
            content_list.append(self._get_content(url, img_path))
            print(f'\tscraping for apartment # {i+1} is done')
        
        df = self._get_df(content_list, save_to_excel=True)
        df.to_csv(f'{data_path}/coldwell_dot_com.csv')
        print('job done!')

### Compass For Rent
class compass_dot_com:

    def __init__(self, city, state):
        self._city = city.lower().replace(' ', '-')
        self._state = state.lower()
        self._url = f'https://www.compass.com/for-rent/{self._city}-{self._state}/'
        self._browser, _ = self._get_browser(self._url)

    @staticmethod
    def _build_options():
        options = webdriver.ChromeOptions()
        options.accept_untrusted_certs = True
        options.assume_untrusted_cert_issuer = True

        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-impl-side-painting")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-seccomp-filter-sandbox")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-cast")
        options.add_argument("--disable-cast-streaming-hw-encoding")
        options.add_argument("--disable-cloud-import")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-ipv6")
        options.add_argument("--allow-http-screen-capture")
        options.add_argument("--start-maximized")
        options.add_argument('--lang=es')

        return options

    def _get_browser(self, webpage):
        """
        A helper function to get the selenium browser in order 
        to perform the scraping tasks 

        Parameters
        ----------
        chromedriver : str
            the path to the location of the chromedriver 

        Returns
        -------
        browser : webdriver.Chrome
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """
        options = self._build_options()
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

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

    ### get all the apartment URLs 
    def _get_apt_urls(self, test=False):
        apt_urls = []
        browser = self._browser
        try:
            while True:
                # search all the tags in the gallary, usually 20 apartments per page
                atags = browser.find_elements_by_xpath("//a[@class='uc-listingPhotoCard uc-listingCard uc-listingCard-has-photo']")
                hrefs = [atag.get_attribute('href') for atag in atags] # fetch the url to the details of a apartment
                apt_urls += hrefs
                button = browser.find_element_by_xpath("//button[@data-tn='arrowButtonRight']") # click through the right button
                button.click() # click until the last possible right arrow 

                if test == True:
                    return apt_urls
        except:
            # if the last page is reached then we can return all the apartment urls that link to the 
            # apartments 
            return apt_urls

    ### aparantly, we are scraping the address 
    def _get_address(self, soup):
        address = soup.find('p', attrs={'data-tn': 'listing-page-address'}) \
                      .get_text()
        if 'unit' in address.lower():
            addr_lst = address.split(',')
            addr = addr_lst[0].strip()
            unit = addr_lst[1].strip()
        else:
            addr = address.strip()
            unit = None

        # manipulate the string that contains a zipcode 
        zipcode = soup.find('div', attrs={'data-tn': 'listing-page-address-subtitle'}) \
                      .get_text() \
                      .split(',')[-1] \
                      .strip() \
                      .split(' ')[-1] \
                      .strip()

        return addr, unit, zipcode

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

    ### a more protective way to access an element from a dictionary
    ### we don't want our program to break if we can't access the 
    ### dictionary from a key 
    def _ad(self, d, k):
        try:
            return d[k]
        except:
            return None

    ### get the price details from the apartments, including price, bath and beds
    def _get_price(self, soup):
        price_tags = soup.find('div', class_='summary__RightContent-e4c4ok-4 bKZPkc u-flexContainer--row') \
                         .find_all('div', class_='summary__StyledSummaryDetailUnit-e4c4ok-13 dsPYTb')

        keys = [tag.find('div', class_='summary__SummaryCaption-e4c4ok-5 fGowyh textIntent-caption2').get_text() for tag in price_tags]
        values = [self._parse_num(tag.find('div', class_='textIntent-title2').get_text()) for tag in price_tags]

        d = dict(zip(keys, values))
        return self._ad(d,'Price'), self._ad(d,'Beds'), self._ad(d,'Bath')

    ### get the square foot of the apartment, this is different from gross square foot 
    def _get_sf(self, soup):
        sqft = soup.find('div', attrs={'data-tn': 'listing-page-summary-sq-ft'}) \
                   .find('div', class_='textIntent-title2') \
                   .get_text()
        sqft = self._parse_num(sqft)
        return sqft

    ### property details, including year built and property type 
    def _get_prop_details(self, soup):
        rows = soup.find_all('tr', class_='keyDetails-text')
        keys = [row.find_all('td')[0].get_text() for row in rows]
        values = [row.find_all('td')[1].get_text() for row in rows]
        d = dict(zip(keys, values))
        return self._ad(d,'Year Built'), self._ad(d,'Compass Type')

    ### building details, including number of units and number of floors 
    def _get_building_details(self, soup):
        try:
            units = soup.find('span', attrs={'data-tn': 'listing-page-building-units'}).get_text()
            stories = soup.find('span', attrs={'data-tn': 'listing-page-building-stories'}).get_text()

            units = int(self._parse_num(units))
            stories = int(self._parse_num(stories))

            return units, stories
        except:
            return None, None

    ### fetch the amenity details
    def _get_amenities(self, apt_url):
        try:
            browser = self._browser
            browser.get(apt_url)
            view_more = browser.find_element_by_xpath("//button[@class='sc-kkGfuU hltMrU cx-nakedBtn textIntent-caption1--strong']")
            view_more.click()
            amenities = browser.find_elements_by_xpath("//span[@data-tn='uc-listing-amenity']")
            amenities = [a.text.lower() for a in amenities]
            central_ac, wd = 0, 0

            for a in amenities:
                if 'Central AC'.lower() in a:
                    central_ac = 1
                if 'Washer / Dryer'.lower() in a:
                    wd = 1
            return central_ac, wd
        except:
            return 0, 0

    def _get_last_price(self, soup):
        try:
            price_tab = soup.find('table', attrs={'data-tn': 'listingHistory-view-eventTable'})
            rows = price_tab.find_all('tr')[1:]
            price_cols = [row.find_all('td')[2].get_text() for row in rows]
            price_cols = [self._parse_num(col) for col in price_cols]
            last_price = list(filter(lambda price: not price==None, price_cols))[0]
            return last_price
        except:
            return None

    def _get_image_urls(self, soup):
        img_tags = soup.find_all('div', attrs={'data-tn': 'undefined-gallery-navigation-navigation-image'})
        img_urls = [itag.find('img')['src'] for itag in img_tags]
        return img_urls

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):

        """
        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # if address is invalid, discontinue the process
            if not address:
                return 0

            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)
            
            # create a folder for the apartment if it doesn't
            # exist inside the section folder
            if not os.path.exists(address):
                os.mkdir(address)
            os.chdir(address)

            # write images inside the apartment folder
            for i, img_url in enumerate(img_urls):
                img_data = requests.get(img_url).content
                with open(f'img{i}.jpg', 'wb') as handler:
                    handler.write(img_data)
                    
            os.chdir(current_path)
            return 1
        except:
            os.chdir(current_path)
            return 0

    def _get_apt_data(self, url, img_path):
        soup = self._get_soup(url)

        city = self._city.replace('-', ' ').title()
        state = self._state.upper()
        addr, unit, zipcode = self._get_address(soup)
        price, beds, bath = self._get_price(soup)
        sqft = self._get_sf(soup)
        yrbuilt, rtype = self._get_prop_details(soup)
        units, stories = self._get_building_details(soup)
        central_ac, wd = self._get_amenities(url)
        last_price = self._get_last_price(soup)

        data = (
            addr, 
            unit, 
            city,
            state,
            zipcode, 
            price, 
            beds, 
            bath, 
            sqft, 
            yrbuilt, 
            rtype,
            units, 
            stories,
            central_ac, 
            wd,
            last_price,
            url,
        )

        img_urls = self._get_image_urls(soup)
        self._save_images(img_urls, img_path, f"{addr}, {self._city.replace('-', ' ').title()}, {self._state.upper()}")

        return data

    def scrape_apt_data(self, urls, img_path):
        apt_data = []

        for url in urls:
            apt_data.append(self._get_apt_data(url, img_path))

        return apt_data

    def write_data(self,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory
        # check if the data exists, if not, create a new data file
        if not os.path.exists('compass_dot_com.csv'):
            df = pd.DataFrame([], columns=CONST.COMPASS_COLNAMES)
            df.to_csv('compass_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.COMPASS_COLNAMES)
        with open('compass_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path, test=False):
        # time of sleep 
        sleep_secs = 15

        # all apartment URLs
        apt_urls = self._get_apt_urls(test=test)

        # divide the apartment URLs list into small batches 
        url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

        # batch jobs start
        print(f'total number of batches: {len(url_batches)}')
        for i, batch in enumerate(url_batches):
            print(f'batch {i} starts, there are {len(batch)} apartment URLs')
            apt_data = self.scrape_apt_data(batch, img_path)
            self.write_data(apt_data, data_path)
            print(f'batch {i} done, sleep {sleep_secs} seconds\n')
            time.sleep(15) # rest for a few seconds after each batch job done

        self._browser.close()
        print('job done, congratulations!')

### Loopnet For Sale
class loopnet_dot_com:

    def __init__(self, city, state):
        self._city = city.replace(' ', '-').lower()
        self._state = state.replace(' ', '-').lower()
        self._url = f'https://www.loopnet.com/{self._state}_multifamily-properties-for-sale/'
        self._browser, _ = self._get_browser('https://www.loopnet.com')

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
    def _get_apt_urls(self, test=False):
        soup = self._get_soup(self._url)
        max_pg = soup.find_all('a', class_='searchPagingBorderless')[-1].text
        max_pg = int(self._parse_num(max_pg))

        apt_urls = []

        for i in range(1, max_pg+1):
            spg = self._get_soup(f'{self._url}{i}/')
            url_tags = spg.find_all('div', class_='listingDescription')
            urls = [['https://www.loopnet.com'+tag.find('a')['href'], tag.find('a')['title']] for tag in url_tags]
            descriptions = [tag.find('span', class_='listingTitle').text for tag in url_tags]
            portfolio = np.array([self._is_portfolio(description) for description in descriptions])
            urls = np.array(urls)
            urls = urls[~portfolio]
            apt_urls += list(urls)

            if test:
                break

        apt_urls = np.array(apt_urls)
        return apt_urls

    def _get_address(self, addr_text):
        addr_list = addr_text.split(',')
        street = addr_list[0].strip()
        city = addr_list[1].strip()
        state = addr_list[2].strip()
        return street, city, state

    ### a more protective way to access an element from a dictionary
    ### we don't want our program to break if we can't access the 
    ### dictionary from a key 
    def _ad(self, d, k):
        try:
            return d[k]
        except:
            return None

    def _unpack_row(self, row_tag):
        cells = row_tag.find_all('td')
        pair1 = (cells[0].text.strip(), cells[1].text.strip())
        if len(cells) == 4:
            pair2 = (cells[2].text.strip(), cells[3].text.strip())
            return [pair1, pair2]
        else:
            return [pair1]

    def _get_apt_data(self, apt_url, img_path):
        addr_text = apt_url[1]
        complete_url = apt_url[0]
        
        street, city, state = self._get_address(addr_text)
        soup = self._get_soup(complete_url)

        data_table = soup.find('section', class_='listing-features') \
                         .find('table', class_='property-data featured-grid')

        rows = data_table.find_all('tr')

        pairs = []

        for row in rows:
            pairs += self._unpack_row(row)

        d = dict(pairs)

        cap_rate = self._parse_num(self._ad(d, 'Cap Rate'))
        if cap_rate:
            cap_rate = cap_rate/100

        prop_type = self._ad(d, 'Property Type')
        units = self._parse_num(self._ad(d, 'No. Units'))
        price = self._parse_num(self._ad(d, 'Price'))
        floors = self._parse_num(self._ad(d, 'No. Stories'))
        gsf = self._parse_num(self._ad(d, 'Building Size'))
        land_sf = self._parse_num(self._ad(d, 'Lot Size'))
        building_class = self._ad(d, 'Building Class')
        year_built = self._ad(d, 'Year Built')
        avg_occ = self._parse_num(self._ad(d, 'Average Occupancy'))

        if avg_occ:
            avg_occ = avg_occ/100

        data = [
            street, 
            city, 
            state,
            cap_rate,
            prop_type,
            units,
            price,
            floors,
            gsf,
            land_sf,
            building_class,
            year_built,
            avg_occ,
            complete_url,
        ]

        img_urls = self._get_img_urls(soup)
        if img_urls:
            self._save_images(img_urls, img_path, f'{street}, {city.title()}, {state.upper()}')

        return data

    def _get_img_urls(self, soup):
        class_list = ['mosaic-tile photo-landscape lazy', 'mosaic-tile photo-portrait lazy']
        img_tags = soup.find_all('div', class_=class_list)
        img_urls = [tag['data-src'] for tag in img_tags]
        return img_urls

    @staticmethod
    def _build_options():
        options = webdriver.ChromeOptions()
        options.accept_untrusted_certs = True
        options.assume_untrusted_cert_issuer = True

        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-impl-side-painting")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-seccomp-filter-sandbox")
        options.add_argument("--disable-breakpad")
        options.add_argument("--disable-client-side-phishing-detection")
        options.add_argument("--disable-cast")
        options.add_argument("--disable-cast-streaming-hw-encoding")
        options.add_argument("--disable-cloud-import")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-session-crashed-bubble")
        options.add_argument("--disable-ipv6")
        options.add_argument("--allow-http-screen-capture")
        options.add_argument("--start-maximized")
        options.add_argument('--lang=es')

        return options

    def _get_browser(self, webpage):
        """
        A helper function to get the selenium browser in order 
        to perform the scraping tasks 

        Parameters
        ----------
        chromedriver : str
            the path to the location of the chromedriver 

        Returns
        -------
        browser : webdriver.Chrome
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """
        options = self._build_options()
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     address):

        """
        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # if address is invalid, discontinue the process
            if not address:
                return 0

            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)
            
            # create a folder for the apartment if it doesn't
            # exist inside the section folder
            if not os.path.exists(address):
                os.mkdir(address)
            os.chdir(address)

            # write images inside the apartment folder
            for i, img_url in enumerate(img_urls):
                browser = self._browser
                browser.get(img_url)
                browser.save_screenshot(f'img{i}.jpg')
                    
            os.chdir(current_path)
            return 1
        except:
            os.chdir(current_path)
            return 0

    def scrape_apt_data(self, apt_urls, img_path):
        apt_data = []

        for url in apt_urls:
            apt_data.append(self._get_apt_data(url, img_path))

        return apt_data

    def write_data(self,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory
        # check if the data exists, if not, create a new data file
        if not os.path.exists('loopnet_dot_com.csv'):
            df = pd.DataFrame([], columns=CONST.LOOPNET_COLNAMES)
            df.to_csv('loopnet_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.LOOPNET_COLNAMES)
        with open('loopnet_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path, test=False):
        # time of sleep 
        sleep_secs = 15

        # all apartment URLs
        apt_urls = self._get_apt_urls(test=test)

        # divide the apartment URLs list into small batches 
        url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

        # batch jobs start
        print(f'total number of batches: {len(url_batches)}')
        for i, batch in enumerate(url_batches):
            print(f'batch {i} starts, there are {len(batch)} apartment URLs')
            apt_data = self.scrape_apt_data(batch, img_path)
            self.write_data(apt_data, data_path)
            print(f'batch {i} done, sleep {sleep_secs} seconds\n')
            time.sleep(15) # rest for a few seconds after each batch job done

        self._browser.close()
        print('job done, congratulations!')

if __name__ == '__main__':

    data_path = '../../data/sample/info'
    img_path = '../../data/sample/images'

    is_testing = True

    ### loopnet.com New York For Sale 
    ldc = loopnet_dot_com('new york', 'new york')
    ldc.scraping_pipeline(data_path, img_path, test=is_testing)

    ### remax.com Philadelphia For Sale
    rmdc = remax_dot_com('philadelphia', 'pa')
    rmdc.scraping_pipeline(data_path, img_path, test=is_testing)

    ### compass New York For Rent 
    codc = compass_dot_com('new york', 'ny')
    codc.scraping_pipeline(data_path, img_path, test=is_testing)

    ### rent.com Philadelphia For Rent
    rdc = rent_dot_com('philadelphia', 'pennsylvania')
    rdc.scraping_pipeline(data_path, img_path, test=is_testing)

    ### coldwell Philadelphia For Sale
    cdc = coldwell_dot_com('philadelphia', 'pa', 1, 'max')
    cdc.scraping_pipeline(data_path, img_path, test=is_testing)

    ### elliman.com For Rent 
    edc = elliman_dot_com('new york', 'ny')
    edc.scraping_pipeline(data_path, img_path, test=is_testing)

    ### trulia.com For Rent and For Sale
    tdc = trulia_dot_com('philadelphia', 'pa')
    tdc.scraping_pipeline(data_path, img_path, test=is_testing)