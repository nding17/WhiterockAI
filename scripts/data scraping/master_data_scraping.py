__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.1.0'
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
import datetime
import urllib
import calendar

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait

from dateutil import parser
from us import states
from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
from fake_useragent import UserAgent
from os import listdir
from os.path import isfile, join
from lycleaner import Address_cleaner

### constant, column names etc.
class CONST:
    # for sale 
    ELLIMAN_HEADER = 'https://www.elliman.com'

    ELLIMAN_COLNAMES = (
        'ADDRESS', 
        'CITY',
        'STATE',
        'ZIP',
        'ASKING PRICE',
        'BED', 
        'BATH', 
        'PROPERTY TYPE',
        'GSF',
        'YEAR BUILT',
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
            'PROPERTY TYPE', 
            'LAND SF', 
            'YEAR BUILT',
            'FIREPLACE',
            'CENTRAL AC',
            '# FLOORS',
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
            'PROPERTY TYPE', 
            'LAND SF', 
            'YEAR BUILT',
            'FIREPLACE',
            'CENTRAL AC',
            '# FLOORS',
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
        'ASKING PRICE',
        'BED',
        'BATH',
        'FIREPLACE',
        'GSF',
        'PROPERTY TYPE',
        'YEAR BUILT',
        'LAND SF',
        'WATERFRONT',
        'CENTRAL AC',
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
        'BED', 
        'BATH', 
        'UNIT SF', 
        'YEAR BUILT', 
        'PROPERTY TYPE',
        '# UNITS', 
        '# FLOORS',
        'CENTRAL AC', 
        'WASHER/DRYER',
        'LAST PRICE',
        'LINK',
    )

    COMPASS_FS_COLNAMES = (
        'CITY',
        'STATE',
        'ADDRESS',
        'ZIP',
        'ASKING PRICE', 
        'BED', 
        'BATH',
        'GSF',
        'YEAR BUILT', 
        'PROPERTY TYPE',
        'CENTRAL AC', 
        'WATERFRONT', 
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
        'ASKING PRICE',
        '# FLOORS',
        'GSF',
        'LAND SF',
        'BUILDING CLASS',
        'YEAR BUILT',
        'AVERAGE OCCUPANCY',
        'LINK',
    )

    # for sale
    COLDWELL_COLNAMES = (
        'ADDRESS',
        'CITY', 
        'STATE', 
        'ZIP', 
        'APT #', 
        'BATH',
        'BED', 
        'GSF',
        'ASKING PRICE', 
        'PROPERTY TYPE',
        'LOT SF', 
        'YEAR BUILT', 
        '# FLOORS', 
        'BASEMENT',
        'BASEMENT DESC', 
        'ARCH', 
        'MATERIAL',
        'LINK',
    )

    # for rent
    HOTPADS_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE', 
        'ZIP',
        'BED', 
        'BATH', 
        'UNIT SF',
        'WASHER/DRYER', 
        '# FLOORS', 
        'CENTRAL AC', 
        'YEAR BUILT', 
        'FIREPLACE',
        'LINK',
        'RENT',
        'APT #',
    )

    # for rent 
    APARTMENTS_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE', 
        'ZIP', 
        'YEAR BUILT', 
        '# UNITS', 
        '# FLOORS', 
        'FIREPLACE', 
        'WASHER/DRYER',
        'LINK',
        'BED', 
        'BATH', 
        'RENT', 
        'UNIT SF', 
        'APT #',
    )

    # for sale
    BERKSHIRE_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE', 
        'ZIP',
        'ASKING PRICE', 
        'LAST PRICE',
        'BED',
        'BATH',
        'YEAR BUILT',
        'GSF',
        'PROPERTY TYPE',
        '# FLOORS',
        'CENTRAL AC',
        'WATERFRONT',
        'FIREPLACE',
        'TAX AMOUNT',
        'LAND SF',
        'LINK',
    )

    REALTYTRAC_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE', 
        'ZIP',
        'SALE PRICE', 
        'SALE DATE',
        'PROPERTY TYPE', 
        'BED', 
        'BATH', 
        'GSF',
    )

    ### city name spelled in full, e.g. new york
    ### state name spelled in abbreviation, e.g. ny
    CITY_NAMES ={
        'NYC': {
            'city': 'new york',
            'state': 'ny',
        },

        'PHL': {
            'city': 'philadelphia',
            'state': 'pa',
        },

        'CHI': {
            'city': 'chicago',
            'state': 'il',
        },
    }

### parent class that includes the most commonly used functions 
class dot_com:

    def __init__(self, city):
        self._city = CONST.CITY_NAMES[city]['city']
        self._state = CONST.CITY_NAMES[city]['state']

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
        options.add_argument("--disable-infobars")  

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

        chrome_path = 'C:/Users/jorda/.wdm/drivers/chromedriver/81/win32/chromedriver.exe'
        browser = webdriver.Chrome(executable_path = chrome_path, options=options)

#        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

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
            text = text.replace(',', '')
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan

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

    def write_data(self,
                   apt_data,
                   filename,
                   colnames, 
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
        if not os.path.exists(f'{filename}'):
            df = pd.DataFrame([], columns=colnames)
            df.to_csv(f'{filename}')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=colnames)
        with open(f'{filename}', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    ### a more protective way to access an element from a dictionary
    ### we don't want our program to break if we can't access the 
    ### dictionary from a key 
    def _ad(self, d, k):
        try:
            return d[k]
        except:
            return None

### For Sale 
class elliman_dot_com(dot_com):

    ############################
    # class initiation section #
    ############################

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._apt_urls = []
        self._apt_data = []
        self._browser, _ = self._get_browser('https://www.elliman.com/')

    #############################
    # private functions section #
    #############################

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

        template = f'https://www.elliman.com/newyorkcity/sales/new-york-ny-usa/{pg_num}-pg'
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
        apartments = soup.find_all('div', class_='listing-item__tab-content')
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
        
            if test and pg_num == 2:
                break
            
            if pg_num%50 == 0:
                # sleep 15 seconds for every batch 
                if verbose:
                    print('50 pages scraped, sleep 15 seconds')
                time.sleep(15)
                
            if pg_num == 845:
                break
                
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
        try:
            browser = self._browser
            browser.get(apt_url)
            
            btn = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[@title='Photos']"))        
            )
            
            btn.click()
            
            gallery = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@class='js-thumbnail-wrapper  carousel__thumbnail']"))        
            )
            
            gallery.click()
            
            thumbnail = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='js-carousel-wrapper  js-scroll-carousel-slider  scroll-carousel__slider']"))        
            )
            
            photos = thumbnail.find_elements_by_xpath("//div[@class='carousel__slide  scroll-carousel__item  js-scroll-carousel-item']")
            
            img_urls = [photo.find_element_by_tag_name('img').get_attribute('src') for photo in photos]
            return img_urls
        except:
            return []

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
        street, city, state, zipcode = None, None, None, None
        try:
            # property detail tag
            street = soup.find('div', class_='main-address').get_text().strip()
            # find address tag
            address = soup.find('div', class_='c-address')
            
            # pattern for the address in this website
            locality = address.find_all('span', class_='locality')
            city = locality[0].get_text().strip()
            if len(locality) > 1:
                city = locality[1].get_text().strip()
            state = address.find('span', class_='region').get_text().strip()
            zipcode = address.find('span', class_='postal-code').get_text().strip()
            return street, city, state, zipcode
        except:
            return street, city, state, zipcode

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
            # price tag
            price = soup.find('div', class_='c-price').get_text().replace(',','') # clean up the text
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
        beds, baths, htype = None, None, None

        try:
            ppt_details = soup.find('div', class_='listing-info__items')
            features = ppt_details.find_all('dl', class_='listing-info__box-content')
            features = [feature.get_text() for feature in features]
            
            # try to identify the room type
            for feature in features:
                if 'beds' in feature.lower():
                    beds = self._extract_num(feature)
                if 'baths' in feature.lower():
                    baths = self._extract_num(feature)
                if (not 'beds' in feature.lower()) and \
                   (not 'baths' in feature.lower()) and \
                   (not 'half baths' in feature.lower()):
                    htype = feature.strip()

            return beds, baths, htype
        except:
            return beds, baths, htype

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
        gsf, year_built = None, None
        try:
            ppt_details = soup.find_all('div', class_='m-listing-info')[1]
            all_props = ppt_details.find_all('div', class_='listing-info__box')
            
            keys = [prop.find('dt', attrs={'itemprop': 'name'}).get_text().strip().lower() for prop in all_props]
            values = [prop.find('dd', attrs={'itemprop': 'value'}).get_text() for prop in all_props]
            d = dict(zip(keys, values))
                                    
            gsf = self._extract_num((self._ad(d, 'interior')))
            year_built = self._ad(d, 'year built')
            
            return gsf, year_built
        except:
            return gsf, year_built

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
        street, city, state, zipcode = self._get_address(soup)
        price = self._get_price(soup)
        beds, baths, htype = self._get_features(soup)
        sqft, year_built = self._get_sqft(soup)
        
        # create a list that package all the useful data
        unit = [
            street, 
            city,
            state,
            zipcode,
            price,
            beds, 
            baths, 
            htype,
            sqft,
            year_built,
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
                print(f'FAILED apt url: {url}')
                continue

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
                street, city, state, _ = self._get_address(soup)

                if imgs:
                    # automatically save images onto the local machine 
                    self._save_images(imgs, data_path, f'{street}, {city}, {state.upper()}')
            except:
                # time to give up and try to find what's going on
                print(f'FAILED apt: {street}, url: {url}')
                continue

        if verbose:
            print('all images scraped')

    def scraping_pipeline(self, data_path, img_path, test=False):

        try:
            # time of sleep 
            sleep_secs = 15

            # scrape all the apartment URLs
            # notice the test is opted out here
            self.scrape_apt_urls(verbose=True, test=test)
            apt_urls = self.apt_urls # fetch the apartment URLs

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0 # record where it failed and re-establish connections

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                self.scrape_apt_data(batch, verbose=True, test=test)
                self.scrape_apt_images(batch, img_path, verbose=True, test=test)
                apt_data = self.apt_data
                self.write_data(apt_data, 'elliman_forsale.csv', CONST.ELLIMAN_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done
            self._browser.close()
            print('job done, congratulations!')

        except:
            print('elliman failed, trying to re-establish connection')
            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                self.scrape_apt_data(batch, verbose=True, test=test)
                self.scrape_apt_images(batch, img_path, verbose=True, test=test)
                apt_data = self.apt_data
                self.write_data(apt_data, 'elliman_forsale.csv', CONST.ELLIMAN_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done
            print('job done, congratulations!')
        finally:
            print('lets move on')

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
class rent_dot_com(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._city = self._city.replace(' ', '-').lower()
        self._state = str(states.lookup(self._state)).replace(' ', '-').lower()
        self._overhead = 'https://www.rent.com'
        self._browser, _ = self._get_browser(self._overhead)
        self._apt_urls = []
        self._apt_data = []

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
            try:
                apt_all_data += self._get_apt_info(apt_url, img_path)
                if verbose:
                    print(f'apartments in address {i} all scraped')
            except:
                print(f'failed at {apt_url}')
                continue

        self._apt_data = apt_all_data

    def scraping_pipeline(self, data_path, img_path, test=False, verbose=False):
        try:
            self.scrape_apt_urls(test=test, verbose=verbose)
            urls = self.apt_urls
            # in order to avoid crashes and loses all your data
            # divide the list of URLs in batches and keep updating
            # the csv file once the batch job is finished
            urls_chunk = np.array_split(urls, int(len(urls)//10))

            failed_point = 0 # record where the program gets stuck and re-connect

            # running the batch and keep saving the intermediary 
            # results from the data scraping jobs 
            # each batch contains 10 URLs, but this could be modified
            for i, batch_urls in enumerate(urls_chunk):
                failed_point = i
                self.scrape_apt_data(batch_urls, img_path, verbose=verbose)
                data = self.apt_data
                self.write_data(data, 'rent_forrent.csv', CONST.RENT_COLNAMES, data_path)
                print(f'batch {i} finished running')
            self._browser.close()
            print('job finished!')
        except:
            print('rent failed, trying to re-establish connection')

            for i, batch_urls in enumerate(urls_chunk[failed_point:]):
                self.scrape_apt_data(batch_urls, img_path, verbose=verbose)
                data = self.apt_data
                self.write_data(data, 'rent_forrent.csv', CONST.RENT_COLNAMES, data_path)
                print(f'batch {i+failed_point} finished running')
            self._browser.close()
            print('job finished!')
        finally:
            print('lets move on')

    @property
    def apt_urls(self):
        # serve as a way to show the apt_urls
        return self._apt_urls

    @property
    def apt_data(self):
        # serve as a way to show the apt_data
        return self._apt_data

### For Sale, For Rent
class trulia_dot_com(dot_com):

    ############################
    # class initiation section #
    ############################

    def __init__(self, city, cat):
        dot_com.__init__(self, city)
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
        self._cat = cat

    #############################
    # private functions section #
    #############################

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
        try:
            browser = self._browser
            browser.get(url)
        except:
            print(browser.current_url)

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
            return features
        except:
            return None

    def _check_prop_type(self, features):
        prop_types = ['condo', 
                      'multi family', 
                      'townhouse', 
                      'single family', 
                      'lot land',
                      'mobile']

        prop_type = None

        for feature in features:
            feature = feature.lower()

            for pt in prop_types:
                if pt in feature:
                    prop_type = feature.title()
                    break

        return prop_type

    def _check_lot_size(self, features):

        lot_size = None

        for feature in features:

            feature = feature.lower()
            ACRE = 43560

            if 'lot size:' in feature:
                if 'acres' in feature:
                    lot_size = self._extract_num(feature)
                    break
                if 'sqft' in feature:
                    try:
                        lot_size = self._extract_num(feature)/ACRE
                        break
                    except:
                        lot_size = None
                        break

        return lot_size
                

    def _check_year_built(self, features):

        year_built = None

        for feature in features:
            feature = feature.lower()
            if 'built in' in feature:
                year_built = int(self._extract_num(feature))
                break

        return year_built

    def _check_fireplace(self, features):
        fireplace = 0

        for feature in features:
            feature = feature.lower()
            if 'fireplace' in feature:
                fireplace = 1
                break

        return fireplace

    def _check_central_ac(self, features):
        central_ac = 0

        for feature in features:
            feature = feature.lower()
            if 'cooling system:' in feature:
                coolings = feature.split(':')[1]
                if 'central' in coolings:
                    central_ac = 1
                    break

        return central_ac

    def _check_stories(self, features):
        stories = None
        for feature in features:
            feature = feature.lower()
            if 'stories:' in feature:
                stories = self._extract_num(feature)
                break

        return stories


    def _open_features(self, features):
        
        prop_type, lot_size, year_built, \
            central_ac, fireplace, stories \
                 = self._check_prop_type(features), \
                    self._check_lot_size(features), \
                    self._check_year_built(features), \
                    self._check_central_ac(features), \
                    self._check_fireplace(features), \
                    self._check_stories(features)

        return prop_type, lot_size, year_built, fireplace, central_ac, stories

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
            try:
                jdict = self._load_json(url)
                street, city, state, zipcode = self._get_address(jdict)
                price = self._get_price(jdict)
                bedrooms, bathrooms = self._get_bedrooms_bathrooms(jdict)
                space = self._get_space(jdict)
                features = self._get_apt_features(jdict)
                prop_type, lot_size, year_built, fireplace, central_ac, stories = self._open_features(features)

                apt_info_data.append([
                    street, 
                    city, 
                    state, 
                    zipcode, 
                    price,
                    bedrooms, 
                    bathrooms,
                    space,
                    prop_type, 
                    lot_size, 
                    year_built, 
                    fireplace, 
                    central_ac,
                    stories,
                    url,
                ])
            except:
                print(f'failed URL: {url}')
                continue

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
                print(f'failed URL: {apt_url}')
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
        prop_type, lot_size, year_built, fireplace, central_ac, stories = self._open_features(features)

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
            prop_type, 
            lot_size, 
            year_built, 
            fireplace, 
            central_ac,
            stories,
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
            try:
                sold_data = self._get_sold_info(apt_url)
                apt_info_data.append(sold_data)
    
                if test and i==5:
                    break
            except:
                print(f'failed at {apt_url}')
                continue

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

            if img_urls:
                # write images onto the local machine 
                self._save_images(img_urls, 
                                  data_path, 
                                  f'{address}, {self._city.title()}, {self._state.upper()}')

        if verbose:
            print(f'images in a total number of {len(apt_urls)} apartments have been scraped')

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # different sales categories 
            categories = self._cat

            # scrape different streams of apartments iteratively 
            # could be optimized by parallel programming 
            print(f'scraping for category - {category} starts!')
            self.scrape_apt_urls(category, test=test, verbose=True)

            # divide the apartment URLs list into small batches 
            # in case the program crashes
            apt_urls = tdc.apt_urls[category]
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//20)

            failed_point = 0

            # batch jobs start
            print(f'a total number of {len(url_batches)} batches, category={category}')
            for i, url_batch in enumerate(url_batches):
                try:
                    failed_point = i
                    print(f'batch {i} starts')
                    self.scrape_apt_data(category, url_batch, verbose=True)
                    data = self.apt_data[category]

                    self.write_data(data, f'trulia_{category}.csv', CONST.TRULIA_COLNAMES[category], data_path)
                    self.scrape_apt_images(category, url_batch, img_path, verbose=True)
                except:
                    print(f'batch {i} failed')
                    continue

            self._browser.close()
            print(f'scraping for category - {category} done!')

        except:
            print('trulia failed, trying to re-establish connection')

            for i, url_batch in enumerate(url_batches[failed_point:]):
                try:
                    print(f'batch {i+failed_point} starts')
                    self.scrape_apt_data(category, url_batch, verbose=True)
                    data = self.apt_data[category]

                    self.write_data(data, f'trulia_{category}.csv', CONST.TRULIA_COLNAMES[category], data_path)
                    self.scrape_apt_images(category, url_batch, img_path, verbose=True)
                except:
                    print(f'batch {i+failed_point} failed')
                    continue

            self._browser.close()
            print(f'scraping for category - {category} done!')
        finally:
            print('lets move on')

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
class remax_dot_com(dot_com):

    # initialization - users need to specify a city and state 
    def __init__(self, city):
        dot_com.__init__(self, city)
        self._overhead = 'https://www.remax.com'

        if self._city == 'new york':
            nyc_url = 'https://www.remax.com/homes-for-sale/NY/New-York/city/3651000'
            self._browser, _ = self._get_browser(nyc_url)
        if self._city == 'philadelphia':
            phi_url = 'https://www.remax.com/homes-for-sale/PA/Philadelphia/city/4260000'
            self._browser, _ = self._get_browser(phi_url)
        if self._city == 'chicago':
            chi_url = 'https://www.remax.com/homes-for-sale/IL/Chicago/city/1714000'
            self._browser, _ = self._get_browser(chi_url)

        self._apt_urls = []
        self._apt_data = []
    
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

        browser = self._browser

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
                btn_next = WebDriverWait(browser, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="__layout"]/div/div[2]/main/div/section[2]/div[2]/div/div[2]/div/button[last()]'))
                )
                btn_next.click()

                if test:
                    self._browser.close()
                    break
        except:
            self._browser.close()
            pass
        return apt_urls

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

            price = self._extract_num(price_text)
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

    def _extract_num(self, text):
        text = text.replace(',', '')
        # extract the numerical price value 
        pattern = r'[-+]?\d*\.\d+|\d+'
        number = re.findall(pattern, text)[0]
        # convert the price to float 
        number = float(number)
        return number

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
                    value = self._extract_num(value)
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
        ac = self._access_dict(sidict, 'Cooling')
        tax = self._access_dict(sidict, 'Tax Annual Amount')
        tax_year = self._parse_year(self._access_dict(sidict, 'Tax Year'))

        try:
            if 'central' in ac.lower():
                ac = 1
        except:
            ac = 0

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
            try:
                apt_all_data.append(self._get_apt_info(apt_url, img_path))
            except:
                print(f'failed at {apt_url}')
                continue
        
        self._apt_data = apt_all_data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # scrape all the apartment URLs in Philadelphia
            # status update enabled
            self.scrape_apt_urls(test=test)
            urls = self.apt_urls

            # in order to avoid crashes and loses all your data
            # divide the list of URLs in batches and keep updating
            # the csv file once the batch job is finished
            urls_chuck = np.array_split(urls, int(len(urls))//20)

            failed_point = 0 # trying to re-connect and record where it failed

            print(f'batch jobs started, {len(urls_chuck)} batches in total')

            # running the batch and keep saving the intermediary 
            # results from the data scraping jobs 
            # each batch contains 10 URLs, but this could be modified
            for i, batch_urls in enumerate(urls_chuck):
                failed_point = i
                self.scrape_apt_data(batch_urls, img_path, verbose=True)
                data = self.apt_data
                self.write_data(data, 'remax_forsale.csv', CONST.REMAX_COLNAMES, data_path)
                print(f'batch {i} finished running')

            print('job done!')
        except:
            print('remax failed, trying to re-establish connection')

            for i, batch_urls in enumerate(urls_chuck[failed_point:]):
                self.scrape_apt_data(batch_urls, img_path, verbose=True)
                data = self.apt_data
                self.write_data(data, 'remax_forsale.csv', CONST.REMAX_COLNAMES, data_path)
                print(f'batch {i+failed_point} finished running')
            print('job done!')
        finally:
            print('lets move on')

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
class coldwell_dot_com(dot_com):

    def __init__(self, city, start_page, end_page):
        dot_com.__init__(self, city)
        self._city = self._city.lower().replace(' ', '-')
        self._state = self._state.lower()
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
        
        try:
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
            asking_price = self._extract_num(asking_price)
            
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
    
            data = [
                street,
                city, 
                state, 
                zip_code, 
                apt_num, 
                bathrooms,
                bedrooms, 
                sqt,
                asking_price, 
                listing_type,
                lot_size, 
                year_built, 
                floors, 
                base,
                base_desc, 
                arch_info, 
                material,
                url,
            ]
    
            ##Scrap all the image for each property and store them into each folder
            ##Please change the file_root accordingly when tested
            image_url = []
            for image_link in listing_content.find_all('img', class_="owl-lazy"):
                image_url.append(image_link.get('data-href'))
    
            if image_url:
                self._save_images(image_url, img_path, f'{street}, {city.title()}, {state.upper()}')
                
            return data
        
        except:
            print(f'no data available at {url}')
            return None

    def _get_max_page(self):
        url = f'https://www.coldwellbankerhomes.com/{self._state}/{self._city}/?sortId=2&offset=0'
        content = self._get_link_content(url)
        pg_list = content.find('ul', class_='propertysearch-results-pager')
        pages = pg_list.find_all('li')
        max_pg = pages[-2].get_text()
        return int(max_pg)

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
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

            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = listing_link

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)
            print(f'total number of batches: {len(url_batches)}')

            failed_point = 0 # record where the program breaks

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                try:
                    failed_point = i
                    print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                    apt_data = [self._get_content(url, img_path) for url in batch]
                    apt_data = list(filter(None, apt_data))
                    self.write_data(apt_data, 'coldwell_forsale.csv', CONST.COLDWELL_COLNAMES, data_path)
                    print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                    time.sleep(15) # rest for a few seconds after each batch job done
                except:
                    print(f'batch {failed_point} failed')
                    continue

            print('job done, congratulations!')
        except:
            print('coldwell failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = [self._get_content(url, img_path) for url in batch]
                self.write_data(apt_data, 'coldwell_forsale.csv', CONST.COLDWELL_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            print('job done, congratulations!')
        finally:
            print('lets move on')

### Compass For Rent
class compass_dot_com(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._city = self._city.lower().replace(' ', '-')
        self._state = self._state.lower()
        self._url = f'https://www.compass.com/for-rent/{self._city}-{self._state}/'
        self._browser, _ = self._get_browser(self._url)

    ### get all the apartment URLs 
    def _get_apt_urls(self, test=False):
        apt_urls = []
        browser = self._browser

        max_pg = browser.find_elements_by_xpath("//button[@class='cx-enclosedBtn cx-enclosedBtn--xs']")[-1]
        max_pg = int(self._extract_num(max_pg.text))

        for i in range(max_pg+1):
            url = f'{self._url}start={i*20}/'
            browser.get(url)
            atags = browser.find_elements_by_xpath("//a[@class='uc-listingPhotoCard uc-listingCard uc-listingCard-has-photo']")
            hrefs = [atag.get_attribute('href') for atag in atags] # fetch the url to the details of a apartment
            apt_urls += hrefs
            
            if test:
                break

        print(f'total number of apartments: {len(set(apt_urls))}')
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

    ### get the price details from the apartments, including price, bath and beds
    def _get_price(self, soup):
        try:
            price_tags = soup.find('div', class_='summary__RightContent-e4c4ok-4 chisNx u-flexContainer--row') \
                             .find_all('div', class_='summary__StyledSummaryDetailUnit-e4c4ok-13 dsPYTb')

            keys = [tag.find('div', class_='summary__SummaryCaption-e4c4ok-5 fGowyh textIntent-caption1').get_text() for tag in price_tags]
            values = [self._extract_num(tag.find('div', class_='textIntent-title2').get_text()) for tag in price_tags]

            d = dict(zip(keys, values))
            return self._ad(d,'Price'), self._ad(d,'Beds'), self._ad(d,'Bath')
        except:
            return None, None, None

    ### get the square foot of the apartment, this is different from gross square foot 
    def _get_sf(self, soup):
        try:
            sqft = soup.find('div', attrs={'data-tn': 'listing-page-summary-sq-ft'}) \
                       .find('div', class_='textIntent-title2') \
                       .get_text()
            sqft = self._extract_num(sqft)
            return sqft
        except:
            return None

    ### property details, including year built and property type 
    def _get_prop_details(self, soup):
        try:
            rows = soup.find_all('tr', class_='keyDetails-text')
            keys = [row.find_all('td')[0].get_text() for row in rows]
            values = [row.find_all('td')[1].get_text() for row in rows]
            d = dict(zip(keys, values))
            return self._ad(d,'Year Built'), self._ad(d,'Compass Type')
        except:
            return None, None

    ### building details, including number of units and number of floors 
    def _get_building_details(self, soup):
        try:
            units = soup.find('span', attrs={'data-tn': 'listing-page-building-units'}).get_text()
            stories = soup.find('span', attrs={'data-tn': 'listing-page-building-stories'}).get_text()

            units = int(self._extract_num(units))
            stories = int(self._extract_num(stories))

            return units, stories
        except:
            return None, None

    ### fetch the amenity details
    def _get_amenities(self, apt_url):
        try:
            browser = self._browser
            browser.get(apt_url)
            view_more = browser.find_element_by_xpath("//button[@class='sc-fzolEj eRcVDD cx-nakedBtn textIntent-caption1--strong']")
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
            price_cols = [self._extract_num(col) for col in price_cols]
            last_price = list(filter(lambda price: not price==None, price_cols))[0]
            return last_price
        except:
            return None

    def _get_image_urls(self, soup):
        img_tags = soup.find_all('div', attrs={'data-tn': 'undefined-gallery-navigation-navigation-image'})
        if img_tags:
            try:
                img_urls = [itag.find('img')['src'] for itag in img_tags]
                return img_urls
            except:
                img_urls = [itag.find('img')['data-src'] for itag in img_tags]
                return img_urls
        else:
            return []

    def _get_apt_data(self, url, img_path):
        soup = self._soup_attempts(url)

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

        if img_urls:
            self._save_images(img_urls, img_path, f"{addr}, {self._city.replace('-', ' ').title()}, {self._state.upper()}")

        return data

    def scrape_apt_data(self, urls, img_path):
        apt_data = []

        for url in urls:
            try:
                apt_data.append(self._get_apt_data(url, img_path))
            except:
                print(f'failed at {url}')
                continue

        return apt_data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'compass_forrent.csv', CONST.COMPASS_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('compass for rent failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'compass_forrent.csv', CONST.COMPASS_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

### Compass For Sale
class compass_fs_dot_com(compass_dot_com):

    ### slightly different initialization
    ### the majority are the same except for the URL 
    def __init__(self, city):
        dot_com.__init__(self, city)
        self._city = self._city.lower().replace(' ', '-')
        self._state = self._state.lower()
        self._url = f'https://www.compass.com/homes-for-sale/{self._city}-{self._state}/'
        self._browser, _ = self._get_browser(self._url)

    ### get the price details from the apartments, including price, bath and beds
    def _get_price(self, soup):
        price_tags = soup.find('div', class_='summary__RightContent-e4c4ok-4 chisNx u-flexContainer--row') \
                         .find_all('div', class_='summary__StyledSummaryDetailUnit-e4c4ok-13 dsPYTb')

        keys = [tag.find('div', class_='summary__SummaryCaption-e4c4ok-5 fGowyh textIntent-caption1').get_text() for tag in price_tags]
        values = [self._extract_num(tag.find('div', class_='textIntent-title2').get_text()) for tag in price_tags]

        d = dict(zip(keys, values))
        return self._ad(d,'Price'), self._ad(d,'Beds'), self._ad(d,'Baths') # this is what's different from for rent 

    ### get the apartment data for sale; there's some minor differences with
    ### Compass for rent 
    def _get_apt_data(self, url, img_path):
        soup = self._soup_attempts(url)

        city = self._city.replace('-', ' ').title()
        state = self._state.upper()
        addr, _, zipcode = self._get_address(soup)
        price, beds, bath = self._get_price(soup)
        sqft = self._get_sf(soup)
        yrbuilt, rtype = self._get_prop_details(soup)
        central_ac, waterfront = self._get_amenities(soup)

        data = [
            city,
            state,
            addr,
            zipcode,
            price, 
            beds, 
            bath,
            sqft,
            yrbuilt, 
            rtype,
            central_ac, 
            waterfront, 
            url,
        ]

        img_urls = self._get_image_urls(soup)

        if img_urls:
            self._save_images(img_urls, img_path, f"{addr}, {self._city.replace('-', ' ').title()}, {self._state.upper()}")

        return data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'compass_forsale.csv', CONST.COMPASS_FS_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('compass for sale failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'compass_forsale.csv', CONST.COMPASS_FS_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

### Loopnet For Sale
class loopnet_dot_com(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._city = self._city.replace(' ', '-').lower()
        self._state = str(states.lookup(self._state)).replace(' ', '-').lower()
        self._url = f'https://www.loopnet.com/{self._state}_multifamily-properties-for-sale/'
        self._browser, _ = self._get_browser('https://www.loopnet.com')

    def _is_portfolio(self, description):
        description = description.lower()
        if 'portfolio' in description:
            return True
        else:
            return False

    ### get all the urls to access the information of the apartments 
    def _get_apt_urls(self, test=False):
        soup = self._soup_attempts(self._url)
        max_pg = soup.find_all('a', class_='searchPagingBorderless')[-1].text
        max_pg = int(self._extract_num(max_pg))

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

        cap_rate = self._extract_num(self._ad(d, 'Cap Rate'))
        if cap_rate:
            cap_rate = cap_rate/100

        prop_type = self._ad(d, 'Property Type')
        units = self._extract_num(self._ad(d, 'No. Units'))
        price = self._extract_num(self._ad(d, 'Price'))
        floors = self._extract_num(self._ad(d, 'No. Stories'))
        gsf = self._extract_num(self._ad(d, 'Building Size'))
        land_sf = self._extract_num(self._ad(d, 'Lot Size'))
        building_class = self._ad(d, 'Building Class')
        year_built = self._ad(d, 'Year Built')
        avg_occ = self._extract_num(self._ad(d, 'Average Occupancy'))

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
            try:
                apt_data.append(self._get_apt_data(url, img_path))
            except:
                print(f'failed at {url}')

        return apt_data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0 # record where the program breaks for reconnection

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'loopnet_forsale.csv', CONST.LOOPNET_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('loopnet failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'loopnet_forsale.csv', CONST.LOOPNET_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

### Hotpads For Rent
class hotpads_dot_com(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._city = self._city.replace(' ', '-')
        self._url = f'https://hotpads.com/{self._city}-{self._state}/apartments-for-rent'
        self._browser, _ = self._get_browser(self._url)


    def _get_apt_urls(self, test=False):
        browser = self._browser
        max_pg = browser.find_element_by_xpath("//a[@class='Linker PagerItem PagerContainer-page-number PagerContainer-page-number-total Linker-accent']") \
                        .text

        max_pg = int(self._extract_num(max_pg))

        apt_urls = []

        for i in range(1, max_pg+1):
            browser.get(f'{self._url}/?page={i}')
            containers = browser.find_elements_by_xpath("//div[@class='ListingCard-content-container']")
            atags = [container.find_element_by_tag_name('a') for container in containers]
            hrefs = [a.get_attribute('href') for a in atags]
            apt_urls += hrefs
            time.sleep(3)

            if test:
                break

        return apt_urls

    def _get_address(self, browser):
        addr = browser.find_element_by_tag_name('address') \
                      .text \
                      .split('\n')

        if len(addr)==1:
            addr = browser.find_element_by_xpath("//h1[@class='Text HdpAddress-normal-weight-text Utils-text-overflow Text-sm Text-xlAndUp-md']") \
                          .text \
                          .split('\n')

        if len(addr)>1:
            street = addr[0].strip()
            region = addr[1].strip().split(',')
            city = region[0].strip()
            state = region[1].strip().split(' ')[0]
            zipcode = region[1].strip().split(' ')[1]

            return street, city, state, zipcode

        else:
            return None, None, None, None

    def _get_bed_bath_sqft(self, browser):
        try:
            header_tag = browser.find_element_by_xpath("//div[@class='ModelFloorplanItem-header']")

            bed = header_tag.find_element_by_xpath("//span[@class='ModelFloorplanItem-detail Utils-bold']") \
                            .text
            bed = self._extract_num(bed)

            bath_sqft = header_tag.find_elements_by_xpath("//span[@class='ModelFloorplanItem-bthsqft']")
            bath = self._extract_num(bath_sqft[0].text)
            sf = self._extract_num(bath_sqft[1].text)

            return bed, bath, sf
        except:
            return None, None, None

    # get a list of (price, unit) tuples 
    def _get_price_unit(self, browser):
        empty_units = browser.find_elements_by_xpath("//div[@class='ModelFloorplanItem-empty-unit']")
        if empty_units:
            price_unit = []
            for empty_unit in empty_units:
                rent = self._extract_num(empty_unit.text)
                price_unit.append([rent, None])
        else:
            price_unit = []

            try:
                # view more button
                button_vm = browser.find_element_by_xpath("//*[text()='View more floor plans']")
                button_vm.click()
                button_exp = browser.find_element_by_xpath("//div[@class='ModelFloorplanItem-expand']")
                button_exp.click()
            except:
                pass

            non_empty_units = browser.find_elements_by_xpath("//div[@class='ModelFloorplanItem-unit']")
            for non_empty_unit in non_empty_units:
                price_unit_lst = non_empty_unit.text \
                                               .split('\n') \

                rent = self._extract_num(price_unit_lst[0].strip())
                unit = price_unit_lst[2].strip()

                price_unit.append([rent, unit])

        return price_unit

    def _get_features(self, browser):
        try:
            buttons_sm = browser.find_elements_by_xpath("//div[@class='LinkToggle']")
            for bsm in buttons_sm:
                bsm.click()
        except:
            pass

        feature_tags = browser.find_elements_by_xpath("//li[@class='ListItem']")
        features = [tag.text for tag in feature_tags if tag.text ]

        wd = 0
        if ('Washer' in features) or ('Dryer' in features):
            wd = 1

        stories = None
        for feature in features:
            feature = feature.lower()
            if 'stories:' in feature:
                stories = self._extract_num(feature.split(':')[1])
                break

        central_ac = 0
        for feature in features:
            feature = feature.lower()
            if 'central air conditioning' in feature:
                central_ac = 1
                break

        year_built = None
        for feature in features:
            feature = feature.lower()
            if 'year built:' in feature:
                year_built = feature.split(':')[1].strip()
                break

        fireplace = 0
        if 'Fireplace' in features:
            fireplace = 1

        return wd, stories, central_ac, year_built, fireplace

    def _get_img_urls(self, browser):
        try:
            max_photos = browser.find_element_by_xpath("//div[@class='PhotoCarousel-item-count-badge']") \
                                .text \
                                .split(' ')[-1]
    
            max_photos = int(self._extract_num(max_photos))
            for i in range(max_photos-1):
                button_next = browser.find_element_by_xpath("//div[@class='PhotoCarousel-arrow PhotoCarousel-arrow-right']")
                button_next.click()
    
            photo_tags = browser.find_elements_by_xpath("//img[@class='ImageLoader PhotoCarousel-item']")
            img_urls = [pt.get_attribute('src') for pt in photo_tags]
            return img_urls
        except:
            return []

    def _get_apt_data(self, apt_url, img_path):
        browser = self._browser
        browser.get(apt_url)
        time.sleep(3)

        try:
            robot_check = browser.find_element_by_xpath("//div[@class='page-title']")
            if 'Please verify you are a human' in robot_check.text:
                self._recaptcha(browser)
        except:
            pass

        # get the images, this needs to be happening in the beginning
        # as there are more buttons to be clicked along the way 
        img_urls = self._get_img_urls(browser)

        street, city, state, zipcode = self._get_address(browser)
        bed, bath, sf = self._get_bed_bath_sqft(browser)
        # need to click one button here
        price_unit = self._get_price_unit(browser)
        # one more button to be clicked
        wd, stories, central_ac, year_built, fireplace = self._get_features(browser)

        data = [street, 
                city, 
                state, 
                zipcode,
                bed, 
                bath, 
                sf,
                wd, 
                stories, 
                central_ac, 
                year_built, 
                fireplace,
                apt_url]

        final_data = [data+pu for pu in price_unit]

        if img_urls:
            self._save_images(img_urls, img_path, f'{street}, {self._city.title()}, {self._state.upper()}')

        return final_data

    def scrape_apt_data(self, apt_urls, img_path):
        apt_data = []

        for apt_url in apt_urls:
            try:
                browser = self._browser
                browser.get(apt_url)
                time.sleep(3)
    
                try:
                    robot_check = browser.find_element_by_xpath("//div[@class='page-title']")
                    if 'Please verify you are a human' in robot_check.text:
                        self._recaptcha(browser)
                except:
                    pass
                
                try:
                    multi_units = browser.find_elements_by_xpath("//div[@class='BuildingUnitCard']")
                    print(multi_units.text)
                    unit_urls = [unit.find_element_by_tag_name('a') \
                                     .get_attribute('href') for unit in multi_units]
                    for unit_url in unit_urls:
                        apt_data += self._get_apt_data(unit_url, img_path)
                except:
                    apt_data += self._get_apt_data(apt_url, img_path)
            except:
                print(f'failed at {apt_url}')
                continue

        return apt_data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # time of sleep 
            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0 # record the break point

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'hotpads_forrent.csv', CONST.HOTPADS_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('hotpads failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'hotpads_forrent.csv', CONST.HOTPADS_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

### Apartments For Rent
class apartments_dot_com(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._city = self._city.replace(' ', '-').lower()
        self._state = self._state.lower()
        self._url = f'https://www.apartments.com/{self._city}-{self._state}/'
        self._browser, _ = self._get_browser(self._url)
        
    # choose the right language option
    def _choose_lang(self, browser):
        try:
            lang_button = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//section[@class='languageConfirmation']"))        
            )                     
            
            lang_button.find_element_by_xpath("//button[text()='English']").click()
        except:
            print('no language button')

    # scrape the apartment urls for the entire webpage 
    def _get_apt_urls(self, test=False):
        browser = self._browser
        self._choose_lang(browser)
        max_pg = browser.find_element_by_xpath("//nav[@id='paging']") \
                        .find_elements_by_tag_name('li')[-2] \
                        .text
        max_pg = int(self._extract_num(max_pg))
        apt_urls = []

        for i in range(1, max_pg+1):
            browser.get(f'{self._url}{i}/')
            apts = browser.find_elements_by_xpath("//li/article")
            apt_urls += [apt.get_attribute('data-url') for apt in apts]
            if test:
                break

        return apt_urls

    # address information, street, city, state, zipcode 
    def _get_address(self, browser):
        addr_tags = browser.find_element_by_xpath("//div[@class='propertyAddress']") \
                           .find_elements_by_tag_name("span")

        street = addr_tags[0].text.strip()
        city = addr_tags[1].text.strip()
        state = addr_tags[2].text.strip()
        zipcode = addr_tags[3].text.strip()

        return street, city, state, zipcode

    # get important data for a rental apartment
    def _get_essentials(self, browser):
        try:
            table = browser.find_element_by_xpath("//table[contains(@class, 'availabilityTable')]")

            rows = table.find_elements_by_tag_name('tr')
            rows_data = [[col.text for col in row.find_elements_by_tag_name('td')] for row in rows]
            rows_data = filter(lambda row: row != [], rows_data)

            def _clean_row_data(row):
                row_cleaned = []
                for elem in row:
                    if 'view' in elem.lower():
                        continue
                    elif 'available' in elem.lower():
                        continue
                    elif '' == elem.lower():
                        continue
                    else:
                        row_cleaned.append(elem)
                return row_cleaned

            def _essential_data(row):
                bed = self._extract_num(row[0])
                bath = self._extract_num(row[1])
                rent = self._extract_num(row[2])
                sf, unit = None, None

                if len(row)>3:
                    for r in row[3:5]:
                        if 'sq ft' in r.lower():
                            sf = self._extract_num(r)
                        else:
                            unit = r

                data = [bed, bath, rent, sf, unit,]
                return data

            rdata = [_clean_row_data(row) for row in rows_data]
            edata = [_essential_data(row) for row in rdata]

            return edata
        except:
            return [[None, None, None, None, None]]

    # get property information data
    def _get_prop_info(self, amenities):
        try:
            prop = amenities.find_element_by_xpath("//div[@class='specList propertyFeatures js-spec shuffle-item filtered']") \
                            .find_elements_by_tag_name('li')

            lst = [p.text.strip('•\n') for p in prop]
            year_built, num_units, num_floors = None, None, None

            for l in lst:
                if 'built in' in l.lower():
                    year_built = l.lower().strip('built in').strip()

                if 'units' in l.lower() and 'stories' in l.lower():
                    units_stories = l.lower().split('/')

                    for elem in units_stories:
                        if 'units' in elem.lower():
                            num_units = self._extract_num(elem)
                        if 'stories' in elem.lower():
                            num_stories = self._extract_num(elem)

            return year_built, num_units, num_stories
        except:
            return None, None, None

    # get the add-on features of an apartment such as washer/dryer, fireplace etc.
    def _get_add_ons(self, amenities):
        try:
            add_ons = amenities.find_element_by_xpath("//h3[text()='Features']/parent::div") \
                               .find_elements_by_tag_name('li')

            lst = [a.text.strip('•\n') for a in add_ons]
            fireplace, wd = 0, 0

            for elem in lst:
                if 'fireplace' in elem.lower():
                    fireplace = 1
                if 'washer/dryer' in elem.lower():
                    wd = 1

            return fireplace, wd
        except:
            return None, None

    # return an ensemble of all the features of the apartment 
    def _get_features(self, browser):
        try:
            amenities = browser.find_element_by_xpath("//div[@data-analytics-name='amenities']")
            year_built, num_units, num_stories = self._get_prop_info(amenities)
            fireplace, wd = self._get_add_ons(amenities)
            return year_built, num_units, num_stories, fireplace, wd
        except:
            return None, None, None, None, None

    # grab all the apartment data all at once 
    def _get_apt_data(self, apt_url, img_path):
        browser = self._browser
        browser.get(apt_url)
        street, city, state, zipcode = self._get_address(browser)
        year_built, num_units, num_stories, fireplace, wd = self._get_features(browser)
        
        data = [street, 
                city, 
                state, 
                zipcode, 
                year_built, 
                num_units, 
                num_stories, 
                fireplace, 
                wd,
                apt_url]

        essentials = self._get_essentials(browser)
        final_data = [data+edata for edata in essentials]

        img_urls = self._get_img_urls(browser)
    
        if img_urls:
            self._save_images(img_urls, img_path, f'{street}, {city.title()}, {state.upper()}')

        return final_data

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

    # get the image urls of an apartment
    def _get_img_urls(self, browser):
        try:
            total_imgs = browser.find_element_by_xpath("//div[@class='caption']") \
                                .text
            total_imgs = int(self._extract_num(total_imgs))

            button_g = browser.find_element_by_xpath("//li[@class='item paidImageLarge']")
            button_g.click()

            button_view = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                        (
                            By.XPATH, "//div[@class='headerUtilities'][@id='headerUtilities']"
                        )
                    )
                )

            button_view.click()

            img_urls = []

            try:
                nav = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                            (
                                By.XPATH, "//div[@class='tabWrapper']"
                            )
                        )
                    )
                
                tabs = nav.find_elements_by_tag_name('a')
            except:
                print('no photos')

            for tab in tabs:
                tab.click()
                gallery = WebDriverWait(browser, 10).until(
                    EC.presence_of_element_located(
                            (
                                By.XPATH, "//ul[@class='nano-content']"
                            )
                        )
                    )

                img_tags = gallery.find_elements_by_xpath('li')
                urls = [tag.find_element_by_tag_name('img').get_attribute('src') for tag in img_tags]
                img_urls += urls

            return img_urls
        except:
            return []

    def scrape_apt_data(self, apt_urls, img_path):
        apt_data = []

        for url in apt_urls:
            try:
                apt_data += self._get_apt_data(url, img_path)
            except:
                print(f'failed at {url}')
                continue

        return apt_data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'apartments_forrent.csv', CONST.APARTMENTS_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('apartments failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'apartments_forrent.csv', CONST.APARTMENTS_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

### Berkshire Hathaway For Sale
class berkshire_dot_com(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._url = 'https://www.bhhs.com/'
        self._browser, _ = self._get_browser(self._url)

    def _accept_cookies(self, browser):
        try:
            cookies = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                        (
                            By.XPATH, "//button[@title='Accept Cookies Button']"
                        )
                    )
                )
            cookies.click()
        except:
            print('no cookies to be accpted')
            pass

    # instead of inputting a fixed URL, use Selenium
    # to search the keyword would be much more bug-free
    def _search(self, browser):
        self._accept_cookies(browser)   
        query = f'{self._city.title()}, {self._state.upper()}'
        sbar = browser.find_element_by_xpath("//input[@class='cmp-search-suggester__input']")
        sbar.clear()
        sbar.send_keys(query)
        
        try:
            # wait until the drop off list appears 
            dropoff = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                        (
                            By.XPATH, f"//li[contains(text(),'"+query+"')]"
                        )
                    )
                )

            dropoff.click()
        except:
            # drop off list does not appear as expected
            # input the query again
            sbar.clear()
            sbar.send_keys(query)

            # wait until the drop off list appears 
            dropoff = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                        (
                            By.XPATH, f"//li[contains(text(),'"+query+"')]"
                        )
                    )
                )

            dropoff.click()

    def _get_apt_urls(self, test=False):
        browser = self._browser
        self._search(browser)

        self._accept_cookies(browser)
        apt_urls = []

        # tag for the next page button
        next_page_tag = "//a[@class='cmp-search-results-pagination__arrow" \
        " cmp-search-results-pagination__arrow--next d-none d-lg-inline-block']"

        try:
            # repeatly hitting the next page button until reaching 
            # the end of the page 
            while True:
                time.sleep(5)
                apts = browser.find_elements_by_xpath("//section[@class='cmp-property-tile']")
                urls = [apt.find_element_by_tag_name('a').get_attribute('href') for apt in apts]
                apt_urls += urls

                next_page = WebDriverWait(browser, 20).until(
                    EC.element_to_be_clickable(
                            (
                                By.XPATH, next_page_tag
                            )
                        )
                    )

                next_page.click()

                if test:
                    return apt_urls

        except:
            # now we know the last page of the apartments 
            # we are looking for is reached 
            print(f'total number of apartments: {len(set(apt_urls))}')
            return apt_urls

    def _get_img_urls(self, browser):
        try:
            img_urls = []
            
            button_exp = WebDriverWait(browser, 5).until(
                    EC.element_to_be_clickable(
                            (
                                By.XPATH, "//a[@class='btn btn-expand']"
                            )
                        )
                    )

            button_exp.click()
            gallery = browser.find_elements_by_xpath("//img[@src='data:']")
            img_urls = [img.get_attribute('data-image') for img in gallery]
            return img_urls
        except:
            return []

    def _get_address(self, browser):
        try:
            address_lst = browser.find_element_by_xpath("//div[@class='address']") \
                                 .text \
                                 .split('\n')

            street = address_lst[0].strip()
            if ',' in address_lst[1]:
                region_lst = address_lst[1].split(',')
                city = region_lst[0].strip()
                state = region_lst[1].strip().split(' ')[0].strip()
                zipcode = region_lst[1].strip().split(' ')[1].strip()
            else:
                city = self._city.title()
                state = self._state.upper()
                zipcode = address_lst[1].strip().split(' ')[1].strip()

            dataa = [street, city, state, zipcode]
            return dataa
        except:
            return [None, None, None, None]

    def _get_prop_details(self, browser):
        keys = browser.find_elements_by_xpath("//div[@class='td label']")
        values = browser.find_elements_by_xpath("//div[@class='td']") 

        ks = [k.text.strip() for k in keys]
        vs = [v.text.strip().replace('\n', ' | ') for v in values]

        pairs = list(zip(ks, vs))

        for i, pair in enumerate(pairs):
            key, value = pair[0], pair[1]
            if key == 'Year Built' and (not value.strip().isdigit()):
                # if the year is not a numerical value
                # delete it since their are two 'year built'
                del pairs[i]

        d = dict(pairs)

        beds = self._extract_num(self._ad(d, 'Beds'))
        bath = self._extract_num(self._ad(d, 'Full Baths'))
        year_built = self._ad(d, 'Year Built')
        sf = self._extract_num(self._ad(d, 'Sq. Ft.'))
        prop_type = self._ad(d, 'Type')
        stroies = self._extract_num(self._ad(d, 'Stories'))
        
        central_ac = 0
        if self._ad(d, 'Central Air') == 'Y':
            central_ac = 1

        waterfront = 0
        if self._ad(d, 'Waterfront') == 'Y':
            waterfront = 1

        fireplace = 0
        fp = self._ad(d, 'Fireplace')
        if fp:
            if 'N' not in fp:
                fireplace = 1

        tax = None
        tax_info = self._ad(d, 'Tax Information')
        if tax_info:
            if 'Annual Amount:' in tax_info:
                tax = self._extract_num(tax_info.split('Annual Amount:')[1])

        land_sf = None
        lot_size = self._ad(d, 'Lot Size')
        if lot_size:
            if ('Sq. Ft.' in lot_size) and ('acres' in lot_size):
                land_sf = self._extract_num(lot_size.split('Sq. Ft.,')[1])
            if ('Sq. Ft.' in lot_size) and ('acres' not in lot_size):
                land_sf = self._extract_num(lot_size)/43560
            if ('Sq. Ft.' not in lot_size) and ('acres' in lot_size):
                land_sf = self._extract_num(lot_size)

        dataf = [
            beds,
            bath,
            year_built,
            sf,
            prop_type,
            stroies,
            central_ac,
            waterfront,
            fireplace,
            tax,
            land_sf,
        ]

        return dataf

    def _get_price_data(self, browser):
        try:
            summary = browser.find_element_by_xpath("//div[@class='cmp-property-details-main-attributes-summary__content']")
            asking_price = summary.find_element_by_xpath("//div[@class='price']").text
            asking_price = self._extract_num(asking_price)

            last_price = None
            history_prices = browser.find_elements_by_xpath("//td[@class='price']")
            if len(history_prices)>1:
                history_prices = [self._extract_num(hp.get_attribute('data-price')) for hp in history_prices]
                for i, price in enumerate(history_prices):
                    if price == asking_price:
                        del history_prices[i]
                last_price = history_prices[0]

            return [asking_price, last_price]
        except:
            return [None, None]

    def _get_apt_data(self, apt_url, img_path):
        browser = self._browser
        browser.get(apt_url)

        dataa = self._get_address(browser)
        dataf = self._get_prop_details(browser)
        datap = self._get_price_data(browser)
        datau = [apt_url]
        final_data = dataa+datap+dataf+datau

        img_urls = self._get_img_urls(browser)
        if img_urls:
            try:
                fn = f'{dataa[0]}, {dataa[1].title()}, {dataa[2].upper()}'
                self._save_images(img_urls, img_path, fn)
            except:
                print('invalid address')

        return final_data

    def scrape_apt_data(self, apt_urls, img_path):
        apt_data = []

        for url in apt_urls:
            try:
                apt_data.append(self._get_apt_data(url, img_path))
            except:
                print(f'failed at {url}')
                continue

        return apt_data

    def scraping_pipeline(self, data_path, img_path, test=False):
        try:
            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'berkshire_forsale.csv', CONST.BERKSHIRE_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('berkshire failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch, img_path)
                self.write_data(apt_data, 'berkshire_forsale.csv', CONST.BERKSHIRE_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

class realtytrac_dot_come(dot_com):

    def __init__(self, city):
        dot_com.__init__(self, city)
        self._url = 'https://www.realtytrac.com/mapsearch/sold/il/cook-county/chicago'
        self._browser, _ = self._get_browser(self._url)

    def _get_apt_urls(self, test=False):
        browser = self._browser
        time.sleep(5)
        last_page = browser.find_element_by_xpath("//a[@class='page']").text.strip('.')
        last_page = int(self._extract_num(last_page))

        apt_urls = []

        for i in range(1, last_page+1):
            browser.get(f'{self._url}/p-{i}')
            time.sleep(6)
            apts = browser.find_elements_by_xpath("//div[@class='LVF-thumb thumb empty-pic img-loadding']")
            urls = [apt.find_element_by_tag_name('a').get_attribute('href') for apt in apts]
            apt_urls += urls

            if test:
                break

        return apt_urls

    def _get_address(self, frame):
        street, city, state, zipcode = None, None, None, None
        try:
            address = frame.find_element_by_xpath("//h1[@itemprop='address']").text

            street = address.split('\n')[0].upper().strip()
            for sep in ['APT', 'UNIT', '#', 'STE']:
                if sep in address.split('\n')[0].upper():
                    street = address.split('\n')[0].upper().split('APT')[0].strip()
                    break

            region = address.split('\n')[1].split(',')
            city = region[0].strip()
            state = region[1].strip().split(' ')[0].strip()
            zipcode = region[1].strip().split(' ')[1].strip()
            return street, city, state, zipcode
        except:
            return street, city, state, zipcode 

    def _get_prop_details(self, frame):
        prop_type, beds, bath, sf = None, None, None, None

        try:
            prop_type = frame.find_element_by_xpath("//address/span[@itemprop='name']").text
            prop_details = frame.find_element_by_xpath("//address/span[@itemprop='description']").text.split(',')
            d = dict()
            for p in prop_details:
                pair = p.strip().split(' ')
                key, value = pair[1].strip().lower(), pair[0].strip()
                d[key] = value

            beds = self._extract_num(self._ad(d, 'beds'))
            bath = self._extract_num(self._ad(d, 'bath'))
            sf = self._extract_num(self._ad(d, 'sqft'))

            return prop_type, beds, bath, sf
        except:
            return prop_type, beds, bath, sf

    def _get_price(self, frame): 
        price, sale_date = None, None
        try:
            price = frame.find_element_by_xpath("//div[@class='price']/span").text
            price = self._extract_num(price)

            sale_date = frame.find_element_by_xpath("//h3[@class='other']").text
            sale_date = str(parser.parse(sale_date, fuzzy_with_tokens=True)[0])

            return price, sale_date
        except:
            return price, 

    def _no_thanks(self, browser):
        try:
            btn_nt = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                        (
                            By.XPATH, "//a[@class='_hj-f5b2a1eb-9b07_survey_close _hj-f5b2a1eb-9b07_transition']"
                        )
                    )
                )

            btn_nt.click()
        except:
            pass
    
    def _get_apt_data(self, apt_url):
        browser = self._browser
        browser.get(apt_url)
        self._no_thanks(browser)

        frame = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable(
                (
                    By.XPATH, "//div[@class='snapshot-container']"
                )
            )
        )

        street, city, state, zipcode = self._get_address(frame)
        price, sale_date = self._get_price(frame)
        prop_type, beds, bath, sf = self._get_prop_details(frame)

        data = [
            street, 
            city, 
            state, 
            zipcode,
            price, 
            sale_date,
            prop_type, 
            beds, 
            bath, 
            sf,
        ]

        return data

    def scrape_apt_data(self, apt_urls):
        apt_data = []

        for url in apt_urls:
            try:
                apt_data.append(self._get_apt_data(url))
            except:
                print(f'failed at {url}')
                continue

        return apt_data

    def scraping_pipeline(self, data_path, test=False):
        try:
            # time of sleep 
            sleep_secs = 15

            # all apartment URLs
            apt_urls = self._get_apt_urls(test=test)

            # divide the apartment URLs list into small batches 
            url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

            failed_point = 0

            # batch jobs start
            print(f'total number of batches: {len(url_batches)}')
            for i, batch in enumerate(url_batches):
                failed_point = i
                print(f'batch {i} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch)
                self.write_data(apt_data, 'realtytrac.csv', CONST.REALTYTRAC_COLNAMES, data_path)
                print(f'batch {i} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        except:
            print('realtytrac failed, trying to re-establish connection')

            for i, batch in enumerate(url_batches[failed_point:]):
                print(f'batch {i+failed_point} starts, there are {len(batch)} apartment URLs')
                apt_data = self.scrape_apt_data(batch)
                self.write_data(apt_data, 'berkshire_forsale.csv', CONST.REALTYTRAC_COLNAMES, data_path)
                print(f'batch {i+failed_point} done, sleep {sleep_secs} seconds\n')
                time.sleep(15) # rest for a few seconds after each batch job done

            self._browser.close()
            print('job done, congratulations!')
        finally:
            print('lets move on')

### merge all the files together 
class data_merger:

    def __init__(self, data_path):
        self._data_path = data_path
        
    def _select_prop(self, prop_type):
        acceptable = ['townhouse', 'single', 'multi']
        accepted = False
        
        for acc in acceptable:
            if acc in str(prop_type).lower():
                accepted = True
                break
        
        if 'condo' in str(prop_type).lower():
            accepted = False
        
        return accepted 

    def merge_super_dfs(self, city):
        files = [f for f in listdir(self._data_path) \
                    if isfile(join(self._data_path, f)) \
                        and '.csv' in f \
                        and 'Super_Master_File' not in f \
                        and 'property_to_estimate' not in f \
                        and 'Rent_Master' not in f]
        
        dfs = []

        for file in files:
            df = pd.read_csv(f'{data_path}/{file}',
                             index_col=0,
                             error_bad_lines=False,
                             encoding= 'unicode_escape')
            df['ADDRESS'] = df['ADDRESS'].astype(str)
            
            if 'forsale' in file:
                df['SELECTED'] = df['PROPERTY TYPE'].apply(self._select_prop)
                df = df[df['SELECTED']==True][df.columns.difference(['SELECTED'])]
                
                df['PROPERTY TYPE'].mask(df['PROPERTY TYPE'].str.contains(pat='townhouse', flags=re.IGNORECASE, regex=True, na=False), 'Townhouse', inplace=True)
                df['PROPERTY TYPE'].mask(df['PROPERTY TYPE'].str.contains(pat='single', flags=re.IGNORECASE, regex=True, na=False), 'Single Family', inplace=True)
                df['PROPERTY TYPE'].mask(df['PROPERTY TYPE'].str.contains(pat='multi', flags=re.IGNORECASE, regex=True, na=False), 'Multi-family', inplace=True)
            
            if 'forrent' in file:
                df['PROPERTY TYPE'] = 'Rental'
            
            dfs.append(df)

        final_df = pd.concat(dfs, 
                             axis=0, 
                             ignore_index=True, 
                             sort=False)
        

        cleaner = Address_cleaner()
        final_df['ADDRESS'] = cleaner.easy_clean(final_df['ADDRESS'].str.upper())

        date_today = str(datetime.date.today())
        final_df.to_csv(f'D:/{city}/master_data/{city} Super_Master_File {date_today}.csv', index=False)

    def merge_forrent_dfs(self, city):
        files = [f for f in listdir(self._data_path) \
                    if isfile(join(self._data_path, f)) \
                        and '.csv' in f \
                        and ('forrent' in f or 'rent' in f) \
                        and 'Super_Master_File' not in f \
                        and 'property_to_estimate' not in f \
                        and 'Rent_Master' not in f]
        dfs = []

        for file in files:
            df = pd.read_csv(f'{data_path}/{file}',
                             index_col=0,
                             error_bad_lines=False,
                             encoding= 'unicode_escape')
            df['ADDRESS'] = df['ADDRESS'].astype(str)
            dfs.append(df)

        final_df = pd.concat(dfs, 
                             axis=0, 
                             ignore_index=True, 
                             sort=False)


        cleaner = Address_cleaner()
        final_df['ADDRESS'] = cleaner.easy_clean(final_df['ADDRESS'].str.upper())
        final_df['PROPERTY TYPE'] = 'Rental'
        
        date_today = str(datetime.date.today())
        final_df.to_csv(f'D:/{city}/master_data/{city} Rent_Master [bylocation;addresses] {date_today}.csv', index=False)

    def merge_forsale_dfs(self, city):
        files = [f for f in listdir(self._data_path) \
                    if isfile(join(self._data_path, f)) \
                        and '.csv' in f \
                        and ('forsale' in f or 'buy' in f) \
                        and 'Super_Master_File' not in f \
                        and 'property_to_estimate' not in f \
                        and 'Rent_Master' not in f]
        dfs = []

        for file in files:
            df = pd.read_csv(f'{data_path}/{file}',
                             index_col=0,
                             error_bad_lines=False,
                             encoding= 'unicode_escape')
            df['ADDRESS'] = df['ADDRESS'].astype(str)
            dfs.append(df)

        final_df = pd.concat(dfs, 
                             axis=0, 
                             ignore_index=True, 
                             sort=False)

        cleaner = Address_cleaner()
        final_df['ADDRESS'] = cleaner.easy_clean(final_df['ADDRESS'].str.upper())
        
        final_df['SELECTED'] = final_df['PROPERTY TYPE'].apply(self._select_prop)
        final_df = final_df[final_df['SELECTED']==True][final_df.columns.difference(['SELECTED'])]
        
        final_df['PROPERTY TYPE'].mask(final_df['PROPERTY TYPE'].str.contains(pat='townhouse', flags=re.IGNORECASE, regex=True, na=False), 'Townhouse', inplace=True)
        final_df['PROPERTY TYPE'].mask(final_df['PROPERTY TYPE'].str.contains(pat='single', flags=re.IGNORECASE, regex=True, na=False), 'Single Family', inplace=True)
        final_df['PROPERTY TYPE'].mask(final_df['PROPERTY TYPE'].str.contains(pat='multi', flags=re.IGNORECASE, regex=True, na=False), 'Multi-family', inplace=True)

        date_today = str(datetime.date.today())
        final_df.to_csv(f'D:/{city}/master_data/property_to_estimate_{city} {date_today}.csv', index=False)

if __name__ == '__main__':
    """
    when you pass in city and state, please make sure
    the following conditions are met:
        1. city name spelled in full
            e.g. new york
        2. state name spelled in abbreviation
            e.g. ny (NOT New York)
    """
    
    major_cities = ['NYC', 'CHI', 'PHL']
    
    for major_city in major_cities:
    
        # user need to provide these paths 
        # please also make sure you have the sub-folders
        # under img_path, for example, remax, rent etc. 
        data_path = f'D:/scrap_data/{major_city}/info/2020-4'
        img_path = f'D:/scrap_data/{major_city}/images'
        
        # to run the scraping for the entire webpage 
        # turn this to False
        is_testing = False
        
        # berkshire hathaway New York For Sale
        bdc = berkshire_dot_com(major_city)
        bdc.scraping_pipeline(data_path, f'{img_path}/berkshire', test=is_testing)
    
        ### remax.com Philadelphia For Sale
        rmdc = remax_dot_com(major_city)
        rmdc.scraping_pipeline(data_path, f'{img_path}/remax', test=is_testing)
        
        ### apartments.com New York For Rent
        adc = apartments_dot_com(major_city)
        adc.scraping_pipeline(data_path, f'{img_path}/apartments', test=is_testing)
       
        ### compass New York For Rent 
        codc = compass_dot_com(major_city)
        codc.scraping_pipeline(data_path, f'{img_path}/compass', test=is_testing)
    
        ### compass New York For Sale 
        codcv2 = compass_fs_dot_com(major_city)
        codcv2.scraping_pipeline(data_path, f'{img_path}/compass', test=is_testing)
       
        ### elliman.com For Sale 
        if major_city == 'NYC':
            edc = elliman_dot_com(major_city)
            edc.scraping_pipeline(data_path, f'{img_path}/elliman', test=is_testing)
       
        ### loopnet.com New York For Sale 
        ldc = loopnet_dot_com(major_city)
        ldc.scraping_pipeline(data_path, f'{img_path}/loopnet', test=is_testing)
       
        ### rent.com Philadelphia For Rent
        rdc = rent_dot_com(major_city)
        rdc.scraping_pipeline(data_path, f'{img_path}/rent', test=is_testing)
    
        ### merge all the datafiles into a master data file 
        dm = data_merger(data_path)
        dm.merge_super_dfs(major_city)
        dm.merge_forsale_dfs(major_city)
        dm.merge_forrent_dfs(major_city)
    #     
    #     if major_city == 'CHI':
    #         rcdc = realtytrac_dot_come('CHI')
    #         rcdc.scraping_pipeline(data_path, test=is_testing)
    # 
    #     ### trulia.com For Rent and For Sale
    #     tdc = trulia_dot_com(major_city, 'buy')
    #     tdc.scraping_pipeline(data_path, f'{img_path}/trulia', test=is_testing)
    #    
    #     ### trulia.com For Rent and For Rent
    #     tdc = trulia_dot_com(major_city, 'rent')
    #     tdc.scraping_pipeline(data_path, f'{img_path}/trulia', test=is_testing)
    #    
    #     ### trulia.com For Rent and Sold
    #     tdc = trulia_dot_com(major_city, 'sold')
    #     tdc.scraping_pipeline(data_path, f'{img_path}/trulia', test=is_testing)
    # 
    #     ### hotpads.com For Rent
    #     hdc = hotpads_dot_com(major_city)
    #     hdc.scraping_pipeline(data_path, f'{img_path}/hotpads', test=is_testing)
    
    #     ### coldwell Philadelphia For Sale
    #     cdc = coldwell_dot_com(major_city, 1, 'max')
    #     cdc.scraping_pipeline(data_path, f'{img_path}/coldwell', test=is_testing)
