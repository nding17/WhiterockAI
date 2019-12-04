import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import time
import os
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


class CONST:
    MAIN_QUERY = 'https://www.corcoran.com/nyc-real-estate/for-sale/search?'\
                  'neighborhoods=battery-park-city%2Cbeekman%2Ccentral-park-south'\
                  '%2Cchelsea-hudson-yards%2Cchinatown%2Cclinton%2Ceast-harlem'\
                  '%2Ceast-village%2Cfinancial-district%2Cflatiron%2Cgramercy'\
                  '%2Cgreenwich-village%2Chamilton-heights%2Charlem%2Cinwood'\
                  '%2Clower-east-side%2Cmidtown-east%2Cmidtown-west'\
                  '%2Cmorningside-heights%2Cmurray-hill%2Croosevelt-island'\
                  '%2Csoho-nolita%2Csutton-area%2Ctribeca%2Cupper-east-side'\
                  '%2Cupper-west-side%2Cwashington-heights%2Cwest-village'\
                  '%2Ccarnegie-hill%2Ckips-bay%2Cno-mad%2Cbath-beach%2Cbensonhurst'\
                  '%2Cbay-ridge%2Cbedford-stuyvesant%2Cbergen-beach%2Cboerum-hill'\
                  '%2Cborough-park%2Cbrighton-beach%2Cbrooklyn-heights%2Cbrownsville'\
                  '%2Cbushwick%2Ccanarsie%2Ccarroll-gardens%2Cclinton-hill%2Ccobble-hill'\
                  '%2Cconey-island%2Ccrown-heights%2Ccypress-hill%2Cditmas-park'\
                  '%2Cdowntown-brooklyn%2Cdyker-heights%2Ceast-flatbush%2Ceast-new-york'\
                  '%2Cflatbush%2Cflatlands%2Cfort-greene%2Cgowanus%2Cgravesend'\
                  '%2Cgreenpoint%2Cgreenwood%2Ckensington%2Clefferts-gardens'\
                  '%2Cmanhattan-beach%2Cmapleton%2Cmarine-park%2Cmidwood'\
                  '%2Cmill-basin%2Cnew-lots%2Cpark-slope%2Cprospect-heights'\
                  '%2Cprospect-park-south%2Cred-hook%2Csea-gate%2Csheepshead-bay'\
                  '%2Cspring-creek%2Cstarrett-city%2Csunset-park%2Cdumbo-vinegar-hill'\
                  '%2Cweeksville%2Cwilliamsburg%2Cwindsor-terrace%2Cocean-parkway'\
                  '%2Cgerritsen-beach%2Cbrooklyn-navy-yard%2Ccolumbia-waterfront'\
                  '%2Castoria%2Cbelle-harbor%2Cforest-hills%2Cjackson-heights%2Ckew-gardens'\
                  '%2Clong-island-city%2Csunnyside%2Cwoodside%2Cridgewood%2Cflushing'\
                  '%2Cfresh-meadows%2Cjamaica%2Csouth-jamaica%2Cmaspeth%2Cglendale'\
                  '%2Cmiddle-village%2Cwoodhaven%2Celmhurst%2Ceast-elmhurst%2Ccorona'\
                  '%2Ccollege-point%2Cwhitestone%2Cqueens-village%2Cbellerose%2Chollis'\
                  '%2Cst-albans%2Ccambria-heights%2Cozone-park%2Csouth-ozone-park'\
                  '%2Choward-beach%2Crichmond-hills%2Cspringfield-gardens%2Claurelton'\
                  '%2Crockaway-beach%2Cbriarwood%2Cbroad-channel%2Cfloral-park%2Cglen-oaks'\
                  '%2Cjamaica-hills%2Ckew-gardens-hills%2Clittle-neck%2Cnew-hyde-park'\
                  '%2Crego-park%2Crochdale%2Crockaway%2Crosedale%2Criverdale%2Callerton'\
                  '%2Cbaychester%2Cbedford-park%2Cbelmont%2Ccastle-hill%2Ccity-island'\
                  '%2Cco-op-city%2Ccountry-club%2Ceast-tremont%2Ceastchester%2Cedenwald'\
                  '%2Cedgewater-park%2Cfordham%2Chighbridge%2Chunts-point%2Ckingsbridge'\
                  '%2Claconia%2Clongwood%2Cmelrose%2Cmorris-heights%2Cmorris-park%2Cmorrisania'\
                  '%2Cmott-haven%2Cnorwood%2Cparkchester%2Cpelham-bay%2Cpelham-gardens'\
                  '%2Cpelham-parkway%2Cschuylerville%2Csoundview%2Cthroggs-neck%2Ctremont'\
                  '%2Cuniversity-heights%2Cvan-nest%2Cwakefield%2Cwilliamsbridge'\
                  '%2Cwoodlawn&keywordSearch=houses%2Ctownhouses'

    COLNAMES = [
        'ADDRESS',
        'CITY', 
        'STATE', 
        'LISTING TYPE',
        'LISTING ID',
        'BEDROOMS', 
        'BATHROOMS', 
        'FLOORS', 
        '# UNITS', 
        'WIDTH', 
        'SF',
        'ASKING PRICE',
    ]

class corcoran_dot_com:

    ############################
    # class initiation section #
    ############################

    def __init__(self, chromedriver):
        self._apt_urls = []
        self._apt_data = []
        self._chromedriver = chromedriver

    #############################
    # private functions section #
    #############################

    def _random_user_agent(self):
        try:
            ua = UserAgent()
            return ua.random
        except:
            default_ua = 'Mozilla/5.0 (Macintosh; Intel Mac O21S X 10_12_3) \
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

    def _soup_attempts(self, url, total_attempts=5):

        soup = self._get_soup(url)

        if soup:
            return soup
        else:
            attempts = 0
            while attempts < total_attempts:
                time.sleep(3)
                soup = self._get_soup(url)
                if soup:
                    return soup
            raise ValueError(f'FAILED to get soup for apt url {url}')

    def _get_apt_url(self, apt_path, wait):
        try:
            url_path = "a[@class='ListingCard__TopSectionLink-k9s72e-17 icXLMN']"
            full_path = f'{apt_path}/{url_path}'
            element = wait.until(EC.presence_of_element_located((By.XPATH, full_path)))
            href = element.get_attribute('href')
            return href 
        except:
            print('can not find apartment')
            return None

    def _get_apt_url_batches(self, start, end, wait):
        results_batch = []
        for i in range(start, end):
            sibling_path = f"//div[@class='ListingCard__ListingCardWrapper-k9s72e-7 bxPua']/following-sibling::div[{i}]"
            href = self._get_apt_url(sibling_path, wait)
            results_batch.append(href)
        return results_batch 
            
    def _get_total_apt_num(self, url):
        soup = self._soup_attempts(url)
        header = soup.find('h2')\
                     .get_text()
        total_apt_num = int(self._extract_num(header))
        return total_apt_num

    def _buffer_page(self, scroll_pg):
        if scroll_pg <= 10*49:
            scroll_buffer = scroll_pg+5
        elif scroll_pg <= 16*49:
            scroll_buffer = scroll_pg+10
        elif scroll_pg <= 21*49:
            scroll_buffer = scroll_pg+15
        elif scroll_pg <= 25*49:
            scroll_buffer = scroll_pg+20
        elif scroll_pg <= 31*49:
            scroll_buffer = scroll_pg+25
        else:
            scroll_buffer = scroll_pg+30
        
        return scroll_buffer

    def _get_browser(self, chromedriver):
        browser = webdriver.Chrome(executable_path=chromedriver)
        browser.get(CONST.MAIN_QUERY)
        wait = WebDriverWait(browser, 20)
        return browser, wait
            
    def _scroll_down(self, scroll_pg, browser, wait):
        try:
            dest = f"//div[@class='ListingCard__ListingCardWrapper-k9s72e-7 bxPua']/following-sibling::div[{scroll_pg}]"
            browser.implicitly_wait(5)
            elem_dest = wait.until(EC.presence_of_element_located((By.XPATH, dest)))
            browser.execute_script('arguments[0].scrollIntoView(true)', elem_dest)
            time.sleep(5)
            scroll_buffer = self._buffer_page(scroll_pg)
            
            buffer_dest = f"//div[@class='ListingCard__ListingCardWrapper-k9s72e-7 bxPua']/following-sibling::div[{scroll_buffer}]"
            browser.implicitly_wait(5)
            elem_buffer = wait.until(EC.presence_of_element_located((By.XPATH, buffer_dest)))
            browser.execute_script('arguments[0].scrollIntoView(true)', elem_buffer)
        except:
            print(f'scrolling failed')

    def _keep_scrolling_down(self, 
                             total_apt_num, 
                             browser, 
                             wait, 
                             verbose=False, 
                             test=False):
        nbatches = int((total_apt_num//49)+1)
        results = []
        
        if test:
            nbatches = 5
        
        for i in range(nbatches):
            scroll_pg = 49*(i+1)
            self._scroll_down(scroll_pg, browser, wait)
            if verbose:
                print(f'page {i+1} scrolled')
            
            start, end = 49*i, 49*(i+1)
            if i == 0:
                start = 1
            results += self._get_apt_url_batches(start, end, wait)
            
            if verbose:
                print(f'results for page {i+1} obtained')
                
        return results

    def _get_apt_urls(self,
                      browser, 
                      wait, 
                      verbose=False, 
                      test=False):
        first_apt_path = f"//div[@class='ListingCard__ListingCardWrapper-k9s72e-7 bxPua']"
        first_apt_url = self._get_apt_url(first_apt_path, wait)
        results = [first_apt_url]
        total_apt_num = self._get_total_apt_num(CONST.MAIN_QUERY) 

        results += self._keep_scrolling_down(total_apt_num, 
                                             browser, 
                                             wait, 
                                             verbose, 
                                             test)

        results_final = list(filter(lambda x: x!=None, results))
        return results_final

    def _get_apt_address(self, soup_apt):
        try:
            address = soup_apt.find('div', attrs={'data-name': 'col-md-8'})\
                              .find('h1')\
                              .get_text()
            return address
        except:
            return None

    def _get_apt_listing_type(self, soup_apt):
        try:
            listing_type = soup_apt.find('div', class_='MainListingInfo__UnitTypeAndStatusContainer-sc-1fxwvn8-9 hnYmAD')\
                                   .get_text()\
                                   .split('|')[0]\
                                   .strip()
            return listing_type
        except:
            return None

    def _get_apt_web_id(self, soup_apt):
        try:
            web_id = soup_apt.find('strong', class_='MainListingInfo__WebId-sc-1fxwvn8-4 haTtwu')\
                             .get_text()\
                             .split(':')[1]\
                             .strip()
            return web_id
        except:
            return None

    def _get_apt_essentials(self, soup_apt):
        beds, baths, floors, units, width, sf = None, None, None, None, None, None
        try:
            essentials_tags = soup_apt.find('ul', class_='Essentials__EssentialsWrapper-sc-1jh003w-0 boWTpJ')\
                                      .find_all('li')
            essentials = [etag.get_text().lower() for etag in essentials_tags]
            
            for item in essentials:
                if 'bath' in item:
                    baths = self._extract_num(item)
                if 'bed' in item:
                    beds = self._extract_num(item)
                if 'unit' in item:
                    units = self._extract_num(item)
                if 'width' in item:
                    width = self._extract_num(item)
                if 'sqft' in item:
                    sf = self._extract_num(item)
                if 'floor' in item:
                    floors = self._extract_num(item)
            
            return beds, baths, floors, units, width, sf
        except:
            return beds, baths, floors, units, width, sf

    def _get_apt_price(self, soup_apt):
        try:
            price_text = soup_apt.find('div', attrs={'data-name': 'col-md-4'})\
                                 .get_text()\
                                 .replace('$', '')\
                                 .replace(',', '')
            price = self._extract_num(price_text)
            return price
        except:
            return None

    def _get_apt_data(self, apt_url):
        soup_apt = self._soup_attempts(apt_url)
        address = self._get_apt_address(soup_apt)
        city, state = 'New York', 'NY'
        listing_type = self._get_apt_listing_type(soup_apt)
        web_id = self._get_apt_web_id(soup_apt)
        beds, baths, floors, units, width, sf = self._get_apt_essentials(soup_apt)
        price = self._get_apt_price(soup_apt)

        apt_data = [
            address,
            city, 
            state, 
            listing_type,
            web_id,
            beds, 
            baths, 
            floors, 
            units, 
            width, 
            sf,
            price,
        ]

        return apt_data

    def _get_img_urls_per_apt(self, soup_apt):
        try:
            figure_tags = soup_apt.find_all('figure', class_='getCarouselSlides__SlideFigure-cel6pe-2 jpnhrN')
            img_urls = [ftag.find('img').get('src') for ftag in figure_tags]
            img_urls = [url for url in img_urls if 'google' not in url]
            return img_urls
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

    ############################
    # public functions section #
    ############################

    def scrapt_apt_urls(self, verbose=False, test=False):
        browser, wait = self._get_browser(self._chromedriver)
        self._apt_urls = self._get_apt_urls(browser, 
                                            wait, 
                                            verbose=verbose, 
                                            test=test)

    def scrape_apt_data(self, apt_urls, verbose=False):

        results = []

        for apt_url in apt_urls:
            results.append(self._get_apt_data(apt_url))

        self._apt_data = results

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
        if not os.path.exists('corcoran_dot_com.csv'):
            df = pd.DataFrame([], columns=CONST.COLNAMES)
            df.to_csv('corcoran_dot_com.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.COLNAMES)
        with open('corcoran_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)


    def write_images(self, 
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
                soup = self._soup_attempts(url)
                imgs = self._get_img_urls_per_apt(soup)

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
                street = self._get_apt_address(soup)
                # automatically save images onto the local machine 
                self._save_images(imgs, data_path, street)
            except:
                # time to give up and try to find what's going on
                raise ValueError(f'FAILED apt: {street}, url: {url}')

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
    
    chromedriver = '/Users/itachi/Downloads/Chrome/chromedriver'
    image_path = '../data/sample/corcoran/imgdata'
    data_path = '../data/sample/corcoran'

    cdc = corcoran_dot_com(chromedriver)
    cdc.scrapt_apt_urls(verbose=True)
    apt_urls = cdc.apt_urls
    cdc.scrape_apt_data(apt_urls)
    apt_data = cdc.apt_data
    cdc.write_data(apt_data, data_path)
    cdc.write_images(apt_urls, image_path, verbose=True)
