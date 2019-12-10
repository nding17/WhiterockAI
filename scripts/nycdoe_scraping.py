#!/usr/bin/env python

"""
nycdoe_scraping.py : Scrape the data for all the schools in NYC 
by using Selenium. The program mimics the normal behavior of a 
human browsing a web
The fundamental logic works as follows:
    - click the inital search page, it will pop out a long list
        of school names. The school names are the keys
    - scrape all the school names from the drop down menu from 
        the search box
    - insert the school name into the search box and you will be 
        directed to a different page, specific to the school name
        you put in 
    - scrape the school data in that particular URL, need to click
        through different tabs to expand the sections we want 
    - implement the above steps in batch, and write data onto the
        local machine after each batch job is finished 

Note: 
    when running this script, please make sure that your computer
    does not go into sleep mode. The screen needs to be lit up in
    order for the browser to work automatically 

    Now you don't need to download chromedriver, it will be done 
    automatically
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.2'
__status__ = 'complete'

### package requirements
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
from webdriver_manager.firefox import GeckoDriverManager

### a class that contains all the contants we will be using 
class CONST:
    # department of education URL
    DOE_URL = 'https://tools.nycenet.edu/snapshot/2019/'

    # this is the column names of the data file
    COLNAMES = [
        'SCHOOL NAME',
        'ADDRESS', 
        'BOROUGH', 
        'CITY', 
        'STATE', 
        'ZIP',
        'ENROLLMENT', 
        'ASIAN', 
        'BLACK', 
        'LATINO', 
        'WHITE',
        'ACHIEVEMENT', 
        'ENGLISH', 
        'MATH',
        'TEACHERS',
        'ENVIRONMENT',
        'LEADERSHIP',
        'COMMUNITY',
        'TRUST',
    ]

### main class 
class nyc_doe:

    ############################
    # class initiation section #
    ############################

    def __init__(self):
        self._school_names = []
        self._school_data = []
        self._browser, self._wait = self._get_browser()

    #############################
    # private functions section #
    #############################

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
        browser : webdriver.Firefox
            a chrome web driver 

        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        """

        browser = webdriver.Firefox(executable_path=GeckoDriverManager().install())
        browser.get(CONST.DOE_URL)
        wait = WebDriverWait(browser, 10) # maximum wait time is 20 seconds 
        return browser, wait

    def _get_schools(self, wait):
        """
        A crucial helper function to collect a list of school names whose data
        we will be scraping

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server

        Returns 
        -------
        schools : list()
            A comprehensive list of school names we could obtain from the drop down
            menu of the search box 
        """
        input_box = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'input')))
        input_box.click()
        elem_schools = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'ul')))
        schools = list(filter(lambda x: 'pre-k' not in x.lower(), elem_schools.text.split('\n')))

        # if debug:
        #     print(f'total number of schools: {len(schools)}')

        return schools

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
        
    def _get_school_si_gen_info(self, wait):
        """
        A helper function to get the diversity info from the general information 
        section of the school page 
        """
        enroll, asian, black, hispanic, white = np.nan, np.nan, np.nan, np.nan, np.nan
        try:
            elem_gen_info = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='metric-group gen']")))
            gen_info = elem_gen_info.text.split('\n')

            for item in gen_info:
                if 'enrollment' in item.lower():
                    item = item.replace(',', '')
                    enroll = self._extract_num(item)

                if 'asian' in item.lower():
                    asian = self._extract_num(item)/100

                if 'black' in item.lower():
                    black = self._extract_num(item)/100

                if 'hispanic' in item.lower():
                    hispanic = self._extract_num(item)/100

                if 'white' in item.lower():
                    white = self._extract_num(item)/100
            return enroll, asian, black, hispanic, white   
        except:
            return enroll, asian, black, hispanic, white
        
    def _get_school_si_loc(self, wait):
        """
        A helper function to get the location info from the general information 
        section of the school page 
        """
        address, borough, city, state, zipcode = None, None, 'New York', None, None
        try:
            elem_loc = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='metric-group location']")))
            location = elem_loc.text.split('\n')
            address = location[1]
            regions = location[2].split(', ')
            borough = regions[0]
            state = regions[1].split(' ')[0]
            zipcode = regions[1].split(' ')[1]
            return address, borough, city, state, zipcode
        except:
            return address, borough, city, state, zipcode
            
    def _get_school_si(self, wait):
        """
        A helper function to collect the school's general information, including
        ethnicity data, address etc. 

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server

        Returns
        ------- 
        si : list()
            a list that contains the general information data pertained to a school

        >>> _get_school_si(wait)
        ['333 East 4 Street', 'Manhattan', 'New York', 'NY', 
            '10009', 161.0, 0.12, 0.28, 0.55, 0.04]
        """
        tab_info = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-info']")))
        tab_info.click()
        
        elem_gen_info = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@class='metric-group gen']")))
        gen_info = elem_gen_info.text.split('\n')
        
        enroll, asian, black, hispanic, white = self._get_school_si_gen_info(wait)
        address, borough, city, state, zipcode = self._get_school_si_loc(wait)
        
        si = [
            address, 
            borough, 
            city, 
            state, 
            zipcode,
            enroll, 
            asian, 
            black, 
            hispanic, 
            white,
        ]
        
        return si

    def _get_school_sa_overall(self, wait):
        """
        A helper function to extract the overall rating from the student achievement 
        section 
        """
        try:
            xpath_sa = "//div[@class='fr-tab-content']/div[@class='element-overall-rating']"
            elem_overall = wait.until(EC.presence_of_element_located((By.XPATH, xpath_sa)))
            overall_rating = elem_overall.find_element_by_class_name('rating-description').text
            return overall_rating
        except:
            return None

    def _get_school_sa_engl(self, wait):
        """
        A helper function to extract the English score from the student achievement 
        section 
        """
        try:
            value_path = "div[@class='metric-bignum']/div[@class='school-value']"
            xpath_engl = f"//div[@class='metric-group perf'][h3='English']/{value_path}"
            elem_engl = wait.until(EC.presence_of_element_located((By.XPATH, xpath_engl)))
            engl_score = self._extract_num(elem_engl.text)/100
            return engl_score
        except:
            return None

    def _get_school_sa_math(self, wait):
        """
        A helper function to extract the math score from the student achievement 
        section 
        """
        try:
            value_path = "div[@class='metric-bignum']/div[@class='school-value']"
            xpath_math = f"//div[@class='metric-group perf'][h3='Math']/{value_path}"
            elem_math = wait.until(EC.presence_of_element_located((By.XPATH, xpath_math)))
            math_score = self._extract_num(elem_math.text)/100
            return math_score
        except:
            return None

    def _get_school_sa(self, wait):
        """
        A helper function to obtain data for the student achievement section, including
        rating and scores for English and Math subjects 

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        Returns
        -------
        sa : list()
            data regarding student performance 

        >>> _get_school_sa(wait)
        ['Excellent', 0.80, 0.91]
        """
        tab_sa = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-sa']")))
        tab_sa.click()
        
        overall_rating = self._get_school_sa_overall(wait)
        engl_score = self._get_school_sa_engl(wait)
        math_score = self._get_school_sa_math(wait)
          
        sa = [
            overall_rating, 
            engl_score, 
            math_score,
        ]

        return sa

    def _get_school_ct(self, wait):
        """
        A helper function to obtain the rating for the Collaborative Teachers  
        section

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        Returns
        -------
        list(1)
            a list that contains a single item, which is the rating of the 
            respective section

        >>> _get_school_ct('Eleanor Roosevelt High School - [HS] 02M416')
        'Good'
        """

        try:
            tab_ct = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-ct']")))
            tab_ct.click()
            
            xpath_ct = "//div[@class='fr-tab-content page-bottom']/div[@class='element-overall-rating']"
            elem_ct = wait.until(EC.presence_of_element_located((By.XPATH, xpath_ct)))
            ct_rating = elem_ct.find_element_by_class_name('rating-description').text
            
            return [ct_rating]
        except:
            return [None]

    def _get_school_se(self, wait):
        """
        A helper function to obtain the rating for Strong Family-Community Ties 
        section

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        Returns
        -------
        list(1)
            a list that contains a single item, which is the rating of the 
            respective section

        >>> _get_school_se('Eleanor Roosevelt High School - [HS] 02M416')
        'Excellent'
        """

        try:
            tab_se = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-se']")))
            tab_se.click()
            
            xpath_se = "//div[@class='tab-content print-always']"
            elem_se = wait.until(EC.presence_of_element_located((By.XPATH, xpath_se)))
            se_rating = elem_se.find_element_by_class_name('rating-description').text
            
            return [se_rating]
        except:
            return [None]

    def _get_school_sf(self, wait):
        """
        A helper function to obtain the rating for Strong Family-Community Ties 
        section

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        Returns
        -------
        list(1)
            a list that contains a single item, which is the rating of the 
            respective section

        >>> _get_school_sf('Eleanor Roosevelt High School - [HS] 02M416')
        'Excellent'
        """

        try:
            tab_sf = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-sf']")))
            tab_sf.click()
            
            xpath_sf = "//div[@class='tab-content print-always']"
            elem_sf = wait.until(EC.presence_of_element_located((By.XPATH, xpath_sf)))
            sf_rating = elem_sf.find_element_by_class_name('rating-description').text
            
            return [sf_rating]
        except:
            return [None]

    def _get_school_tr(self, wait):
        """
        A helper function to obtain the rating for Trust section

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        Returns
        -------
        list(1)
            a list that contains a single item, which is the rating of the 
            respective section

        >>> _get_school_tr('Eleanor Roosevelt High School - [HS] 02M416')
        'Good'
        """

        try:
            tab_tr = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-tr']")))
            tab_tr.click()
            
            xpath_tr = "//div[@class='tab-content print-always']"
            elem_tr = wait.until(EC.presence_of_element_located((By.XPATH, xpath_tr)))
            tr_rating = elem_tr.find_element_by_class_name('rating-description').text
            
            return [tr_rating]
        except:
            return [None]

    def _get_school_es(self, wait):
        """
        A helper function to obtain the rating for effective school
        leadership section

        Parameters
        ----------
        wait : WebDriverWait
            this is wait object that allows the program to hang around for a period
            of time since we need some time to listen to the server 

        Returns
        -------
        list(1)
            a list that contains a single item, which is the rating of the 
            respective section

        >>> _get_school_es('Eleanor Roosevelt High School - [HS] 02M416')
        'Good'
        """
        try:
            tab_es = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-es']")))
            tab_es.click()
            
            xpath_es = "//div[@class='tab-content print-always']"
            elem_es = wait.until(EC.presence_of_element_located((By.XPATH, xpath_es)))
            es_rating = elem_es.find_element_by_class_name('rating-description').text
            
            return [es_rating]
        except:
            return [None]

    def _get_school_data(self, browser, school_name):
        """
        A helper function to scrape the data pertained to a specific 
        school based on its name 

        Parameters
        ----------
        browser : webdriver.Firefox
            a chrome web driver 

        school_name : str 
            the school name that you will put into the search box 

        >>> _get_school_data(browser, '333 East 4 Street')
        ['333 East 4 Street', 'Manhattan', 'New York', 'NY', '10009', 
          161.0, 0.12, 0.28, 0.55, 0.04, 'Excellent', 0.62, 0.65, 
          'Excellent', 'Excellent', 'Excellent', 'Excellent', 'Good']
        """
        try:
            # reset browser to the search box 
            browser.get(CONST.DOE_URL)
            wait = WebDriverWait(browser, 8)
            # find the input box 
            input_box = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'input')))
            # send the school name to the search box 
            input_box.send_keys(school_name)
            # wait until the drop down menu appears, means the content has been loaded
            input_clickable = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@id='result-item-0']")))
            input_clickable.click() # click the drop down item

            sn = [school_name]
            si = self._get_school_si(wait) # general info
            sa = self._get_school_sa(wait) # student achievement
            ct = self._get_school_ct(wait) # teachers
            se = self._get_school_se(wait) # environment
            es = self._get_school_es(wait) # leadership
            sf = self._get_school_sf(wait) # community
            tr = self._get_school_tr(wait) # trust
            
            data = sn+si+sa+ct+se+es+sf+tr # aggregate all the data 
            
            return data
        except:
            print(f'failed to scrape data for school {school_name}')
            return None

    def _get_all_schools_data(self, browser, schools):
        """
        A helper function to scrape all the data pertained to a list of 
        schools user specified 

        Parameters
        ----------
        browser : webdriver.Firefox
            a chrome web driver 

        schools : list(str) 
            a list of school names that you will put into the 
            search box 
        """

        schools_data = []
        for school_name in schools:
            # scrape the data for each school
            data = self._get_school_data(browser, school_name)
            # make sure the data contains something 
            if data:
                schools_data.append(data)
            time.sleep(3)

        return schools_data


    ############################
    # public functions section #
    ############################

    def scrape_school_names(self):
        """
        A public function that allows you to call to scrape school names 

        Parameters
        ----------
        None
            no input parameters are needed 

        Returns
        -------
        None
            nothing will be returned, but the attribute _school_names 
            will be updated and all the school names will be stored 
            in this field 
        """

        self._school_names = self._get_schools(self._wait)

    def scrape_school_data(self, school_names):

        """
        A public function that allows you to scrape information for a list
        of schools the users specified 

        Parameters
        ----------
        school_names : list(str)
            a list of school names scraped from the drop down menu of the 
                search box 

        Returns
        -------
        None
            nothing will be returned, but the attribute _school_data will be updated
            and all the school info will be stored in this field 
        """

        self._school_data = self._get_all_schools_data(self._browser, school_names)

    def write_data(self,
                   school_data, 
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
        if not os.path.exists('nyc_doe.csv'):
            df = pd.DataFrame([], columns=CONST.COLNAMES)
            df.to_csv('nyc_doe.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(school_data, columns=CONST.COLNAMES)
        with open('nyc_doe.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)

    #####################
    # public attributes #
    #####################

    @property
    def school_names(self):
        """
        A public attribute that lets you get access to all
        of the school names that need to be scraped.
        """
        return self._school_names

    @property
    def school_data(self):
        return self._school_data


if __name__ == '__main__':
    # users need to specify the directory to the chromedriver 
    # and the path to the data directory
    data_path = '../data/sample/' 

    # construct a scraping object 
    doe = nyc_doe()
    doe.scrape_school_names()
    schools_names = doe.school_names

    # divide the school names list into small batches 
    school_batches = np.array_split(schools_names, int(len(schools_names))//10)
    # time of sleep 
    sleep_secs = 15

    # batch jobs start
    print(f'total number of batches: {len(school_batches)}')
    for i, batch in enumerate(school_batches):
        # scrape data for a batch of schools
        doe.scrape_school_data(batch)
        school_data = doe.school_data
        # write data onto the local machine
        doe.write_data(school_data, data_path)
        print(f'batch {i} done, sleep {sleep_secs} seconds')
        time.sleep(sleep_secs) # rest for a few seconds after each batch job done
    print('job done, congratulations!')
