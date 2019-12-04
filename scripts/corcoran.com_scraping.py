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

class corcoran_dot_com:

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
            
            buffer_dest = f"//div[@class='ListingCard__ListingCardWrapper-k9s72e-7 bxPua']/following-sibling::div[{scroll_pg+5}]"
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

    def _get_apt_img_urls(self, soup_apt):
        try:
            figure_tags = soup_apt.find_all('figure', class_='getCarouselSlides__SlideFigure-cel6pe-2 jpnhrN')
            img_urls = [ftag.find('img').get('src') for ftag in figure_tags]
            img_urls = [url for url in img_urls if 'google' not in url]
            return img_urls
        except:
            return None

if __name__ == '__main__':
    
    chromedriver = '/Users/itachi/Downloads/Chrome/chromedriver'

    cdc = corcoran_dot_com()
    browser, wait = cdc._get_browser(chromedriver)
    cdc._get_apt_urls(browser, 
                      wait, 
                      verbose=True, 
                      test=True)

