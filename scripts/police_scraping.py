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

class CONST:

    POLICE_URL = 'https://www.cityprotect.com/map/list/incidents?toUpdateDate=12%2F18%2F'\
                 '2019&fromUpdateDate=11%2F18%2F2019&pageSize=2000&parentIncidentTypeIds='\
                 '149,150,148,8,97,104,165,98,100,179,178,180,101,99,103,163,168,166,12&zoom'\
                 'Level=16&latitude=39.94761343841498&longitude=-75.15636979615388&days=1,2,3,'\
                 '4,5,6,7&startHour=0&endHour=24&timezone=-05:00'

    COLNAMES = [
        'CASE NUMBER', 
        'CRIME TITLE',
        'ADDRESS',
        'DATE',
        'TIME',
        'AGENCY',
        'DESCRIPTION',
    ]

class police:

    def __init__(self):
        self._crime_data = []
        self._browser, _ = self._get_browser()

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
        browser.get(CONST.POLICE_URL)
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

    def _write_data(self,
                    crime_data, 
                    data_path):

        """
        
        The scraper will automatically write the apartment data onto the local machine. 

        Parameters
        ----------
        school_data : list(object)
            this is a list of school data in raw format and later on will be used 
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
        if not os.path.exists('police.csv'):
            df = pd.DataFrame([], columns=CONST.COLNAMES)
            df.to_csv('police.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(crime_data, columns=CONST.COLNAMES)
        with open('police.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    def scrape_map(self, data_path, left=1, right=1, up=1, down=1):
    
        cases = []
        all_case_number = []

        browser = self._browser
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
            self._write_data(cases, data_path)
        

if __name__ == '__main__':

    data_path = '../data/sample/' 

    p = police()
    p.scrape_map(data_path, left=1, right=1, up=1, down=1)


