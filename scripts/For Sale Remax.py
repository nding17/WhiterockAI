#!/usr/bin/env python

""" 
remax.com_scraping.py : Scrape the apartment rental infomation in remax.com 
all the users need to do is to specify a city and state (abbreivated) and 
it will automatically scrape all the details related to all the apartments 
in the city users are looking at.
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.2'
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class CONST:

    REMAX_COLNAMES = (
        'ADDRESS', 
        'CITY', 
        'STATE', 
        'ZIPCODE',
        'PRICE',
        'BEDROOMS',
        'BATHROOMS',
        'FIREPLACE',
        'LIVING AREA',
        'PROPERTY TYPE',
        'YEAR BUILT',
        'LOT SIZE',
        'WATERFRONT',
        'AC',
        'TAX AMOUNT',
        'TAX YEAR',
    )

class remax_dot_com:

    # initialization - users need to specify a city and state 
    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._overhead = 'https://www.remax.com'
        self._apt_urls = []
        self._apt_data = []

    @staticmethod
    def _build_chrome_options():
        chrome_options = webdriver.ChromeOptions()
        chrome_options.accept_untrusted_certs = True
        chrome_options.assume_untrusted_cert_issuer = True
        
        # chrome configuration
        # More: https://github.com/SeleniumHQ/docker-selenium/issues/89
        # And: https://github.com/SeleniumHQ/docker-selenium/issues/87
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-impl-side-painting")
        chrome_options.add_argument("--disable-setuid-sandbox")
        chrome_options.add_argument("--disable-seccomp-filter-sandbox")
        chrome_options.add_argument("--disable-breakpad")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-cast")
        chrome_options.add_argument("--disable-cast-streaming-hw-encoding")
        chrome_options.add_argument("--disable-cloud-import")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--disable-session-crashed-bubble")
        chrome_options.add_argument("--disable-ipv6")
        chrome_options.add_argument("--allow-http-screen-capture")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument('--lang=es')

        return chrome_options

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
        options = self._build_chrome_options()
        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

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

    def _remax_apt(self, soup):

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
        ]

        return unit

    def _get_apt_info(self, apt_url):

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

        response = requests.get(self._overhead+apt_url)
        results = response.content
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            # append the luxury feature as an additional column
            apt_info = self._remax_apt(soup)

        return apt_info

    def scrape_apt_urls(self):

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

        self._apt_urls = self._get_ensemble_apt_urls()

    def scrape_apt_data(self, apt_urls, verbose=False):

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
            apt_all_data.append(self._get_apt_info(apt_url)) 
        
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

    def scraping_pipeline(self, data_path):
        # scrape all the apartment URLs in Philadelphia
        # status update enabled
        self.scrape_apt_urls()
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
            self.scrape_apt_data(batch_urls, verbose=True)
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
    
if __name__ == '__main__':

    # construct data scraping object, use Philadelphia, PA 
    # as an example
    rmdc = remax_dot_com('philadelphia', 'pa')
    data_path = '../data/sample'
    rmdc.scraping_pipeline(data_path)
