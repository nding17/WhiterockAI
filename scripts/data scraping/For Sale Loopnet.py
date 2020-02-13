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
from urllib import request
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class CONST:

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
    )

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
    def _get_apt_urls(self):
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
        apt_urls = self._get_apt_urls()

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
    ldc = loopnet_dot_com('new york', 'new york')
    data_path = '../../data/sample'
    img_path = '../../data/sample/loopnet'
    ldc.scraping_pipeline(data_path, img_path)