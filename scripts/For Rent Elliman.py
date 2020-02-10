#!/usr/bin/env python

""" 
elliman.com_scraping.py : Scrape the apartment rental infomation in elliman.com 
the users only need to specify the paths to the directory they want to store the 
images as well as the apartment data. 

It will automatically scrape all the details related to all the apartments in the 
city users are looking at, as well as save all the images in the specified directory.
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.2'
__status__ = 'complete'

### package requirements
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

    COLNAMES = [
        'ADDRESS', 
        'NEIGHBORHOOD', 
        'CITY',
        'ASKING PRICE',
        'BEDROOMS', 
        'BATHROOMS', 
        'HALF BATHROOMS',
        'LISTING TYPE',
        'SF',
        'LISTING ID',
    ]

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
        apt_urls = [f'{CONST.HEADER}{url}' for url in apt_urls]
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
            photo_link = f'{CONST.HEADER}{photo_link}'
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
                    imgs_complete.append(f"{CONST.HEADER}{img['src']}")
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

    def _get_apt_data(self, soup):

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
                soup = self._soup_attempts(url)
                unit = self._get_apt_data(soup)

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
            df = pd.DataFrame([], columns=CONST.COLNAMES)
            df.to_csv('elliman_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.COLNAMES)
        with open('elliman_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scraping_pipeline(self, data_path, img_path):
        # time of sleep 
        sleep_secs = 15

        # scrape all the apartment URLs
        # notice the test is opted out here
        self.scrape_apt_urls(verbose=True, test=False)
        apt_urls = self.apt_urls # fetch the apartment URLs

        # divide the apartment URLs list into small batches 
        url_batches = np.array_split(apt_urls, int(len(apt_urls))//10)

        # batch jobs start
        print(f'total number of batches: {len(url_batches)}')
        for i, batch in enumerate(url_batches):
            print(f'batch {i} starts, there are {len(batch)} apartment URLs')
            self.scrape_apt_data(batch, verbose=True)
            self.scrape_apt_images(batch, image_path, verbose=True)
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


if __name__ == '__main__':

    # users need to specifiy the path where you want to
    # store the data by changing img_path and data_path
    # these are the only lines that users need to change
    # the rest will be automatic 
    img_path = '../data/sample/elliman/imgdata'
    data_path = '../data/sample/elliman'

    # construct an elliman_doc_com object to work
    # on the task
    edc = elliman_dot_com()
    edc.scraping_pipeline(data_path, img_path)
