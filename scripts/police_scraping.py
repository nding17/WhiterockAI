import re
import time
import os
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class police:

    def __init__(self):
        self._crime_data = []
        self._browser, _ = self._get_browser()


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

    def _get_browser(self):
        """
        A helper function to get the selenium browser in order 
        to perform the scraping tasks 

        Parameters
        ----------
        chromedriver : str
            the path to the location of the chromedriver 

        Returns
        -------
        browser : webdriver.chrome
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """
        options = self._build_chrome_options()

        browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
        browser.get(police_url)
        wait = WebDriverWait(browser, 10) # maximum wait time is 20 seconds 
        return browser, wait

    def _collect(self, elem):
        case_number = elem.find_element_by_xpath("//*[@id='incident-case-number']").text
        title = elem.find_element_by_xpath("//*[@class='incident-title']").text
        address = elem.find_element_by_xpath("//*[@class='incident-subtitle']").text
        
        date = elem.find_element_by_xpath("//*[@id='incident-date']").text
        time = elem.find_element_by_xpath("//*[@id='incident-time']").text  
        agency = elem.find_element_by_xpath("//*[@id='incident-agency']").text
        description = elem.find_element_by_xpath("//*[@id='incident-description']").text
        
        return [case_number, title, address, date, time, agency, description]

    def _scrape(self, cases, all_case_number, browser):
        scrollHeight = browser.execute_script('return document.getElementById("incidentsList").scrollHeight')
        i=0
        
        while True:
            # if there's no incidents in the selected area
            # find_element_by_xpath report an error
            try:
                test = browser.find_element_by_xpath("//*[@id='incidentsList']/div[1]/ce-incident-item")
                
                # everytime it scroll 50 pixels, if it already exists in the list, skip it.
                while 50*(i) <= scrollHeight:
                    js = f'document.getElementById("incidentsList").scrollTop=50*{i}'
                    browser.execute_script(js)
                    if i == 0:
                        time.sleep(5)

                    elem = browser.find_element_by_xpath("//*[@id='incidentsList']/div[1]/ce-incident-item")
                    infomation = self._collect(elem)
                    if infomation[0] not in all_case_number:
                        cases.append(infomation)
                        all_case_number.append(infomation[0])
                    i += 1

                # scroll to the button of the side page, collect all the remaining incidents
                elem = browser.find_element_by_xpath("//ce-incident-item[@class='ng-star-inserted']")
                final_elems = elem.find_elements_by_xpath("//span[@id='incident-case-number']")

                case_numbers = elem.find_elements_by_xpath("//span[@id='incident-case-number']")
                titles = elem.find_elements_by_xpath("//span[@class='incident-title']")
                addresses = elem.find_elements_by_xpath("//span[@class='incident-subtitle']")
                dates = elem.find_elements_by_xpath("//span[@id='incident-date']")
                times = elem.find_elements_by_xpath("//span[@id='incident-time']")  
                agencies = elem.find_elements_by_xpath("//span[@id='incident-agency']")
                descriptions = elem.find_elements_by_xpath("//span[@id='incident-description']")

                for i in range(len(final_elems)):
                    if case_numbers[i].text not in all_case_number:
                        all_case_number.append(case_numbers[i].text)
                        cases.append([case_numbers[i].text, titles[i].text, \
                                      addresses[i].text, dates[i].text, times[i].text, \
                                  agencies[i].text, descriptions[i].text])
                break
            except:
                print("Oops! This district has no incident!")
                break

        return cases, all_case_number

    def _move(self, browser, direction, times):
        if direction == 'left':
            for i in range(500*times):
                browser.find_element_by_xpath("//*[@id='mapMainContainer']/ce-map-wrapper/div/uwm-universal-web-map/div/div[1]/div[1]")\
                        .send_keys(Keys.LEFT)
                
        elif direction == 'right': 
            for i in range(500*times):
                browser.find_element_by_xpath("//*[@id='mapMainContainer']/ce-map-wrapper/div/uwm-universal-web-map/div/div[1]/div[1]")\
                        .send_keys(Keys.RIGHT)
        
        elif direction == 'up':
            for i in range(400*times):
                browser.find_element_by_xpath("//*[@id='mapMainContainer']/ce-map-wrapper/div/uwm-universal-web-map/div/div[1]/div[1]")\
                        .send_keys(Keys.UP)   
        
        elif direction == 'down':
            for i in range(400*times):
                browser.find_element_by_xpath("//*[@id='mapMainContainer']/ce-map-wrapper/div/uwm-universal-web-map/div/div[1]/div[1]")\
                        .send_keys(Keys.DOWN)

    def scrape_map(self, browser, left=1, right=1, up=1, down=1):
    
        cases = []
        all_case_number = []
        # move to the up-left corner
        self._move(browser, 'left', left)
        self._move(browser, 'up', up)
        time.sleep(5)
        
        for i in range(up+down+1):
            if i%2 == 0:
                for j in range(left+right):
                    cases, all_case_number = self._scrape(cases, all_case_number, browser)
                    self._move(browser, 'right', 1)
                    time.sleep(5)
            elif i%2 == 1:
                for j in range(left+right):
                    cases, all_case_number = self._scrape(cases, all_case_number, browser)
                    self._move(browser, 'left', 1)
                    time.sleep(5) 
            cases, all_case_number = self._scrape(cases, all_case_number, browser)
            self._move(browser, 'down', 1)
            time.sleep(5) 
            
        return cases, all_case_number
    