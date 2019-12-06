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

class CONST:
    DOE_URL = 'https://tools.nycenet.edu/snapshot/2019/'

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

class nyc_doe:

    def __init__(self, chromedriver):
        self._school_names = []
        self._school_data = []
        self._browser, self._wait = self._get_browser(chromedriver)

    def _get_browser(self, chromedriver):
        browser = webdriver.Chrome(executable_path=chromedriver)
        browser.get(CONST.DOE_URL)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

    def _get_schools(self, wait):
        input_box = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'input')))
        input_box.click()
        elem_schools = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'ul')))
        schools = list(filter(lambda x: 'Pre-K' not in x, elem_schools.text.split('\n')))
        return schools

    def _extract_num(self, text):
        try:
            # pattern to find any number (int or float)
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan
        
    def _get_school_si_gen_info(self, wait):
        
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

    def _get_school_sa(self, wait):
        tab_sa = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-sa']")))
        tab_sa.click()
        
        xpath_sa = "//div[@class='fr-tab-content']/div[@class='element-overall-rating']"
        elem_overall = wait.until(EC.presence_of_element_located((By.XPATH, xpath_sa)))
        overall_rating = elem_overall.find_element_by_class_name('rating-description').text
        
        value_path = "div[@class='metric-bignum']/div[@class='school-value']"
        xpath_engl = f"//div[@class='metric-group perf'][h3='English']/{value_path}"
        elem_engl = wait.until(EC.presence_of_element_located((By.XPATH, xpath_engl)))
        xpath_math = f"//div[@class='metric-group perf'][h3='Math']/{value_path}"
        elem_math = wait.until(EC.presence_of_element_located((By.XPATH, xpath_math)))
        
        math_score = self._extract_num(elem_math.text)/100
        engl_score = self._extract_num(elem_engl.text)/100
        
        sa = [
            overall_rating, 
            engl_score, 
            math_score,
        ]

        return sa

    def _get_school_ct(self, wait):
        tab_ct = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-ct']")))
        tab_ct.click()
        
        xpath_ct = "//div[@class='fr-tab-content page-bottom']/div[@class='element-overall-rating']"
        elem_ct = wait.until(EC.presence_of_element_located((By.XPATH, xpath_ct)))
        ct_rating = elem_ct.find_element_by_class_name('rating-description').text
        
        return [ct_rating]

    def _get_school_se(self, wait):
        tab_se = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-se']")))
        tab_se.click()
        
        xpath_se = "//div[@class='tab-content print-always']"
        elem_se = wait.until(EC.presence_of_element_located((By.XPATH, xpath_se)))
        se_rating = elem_se.find_element_by_class_name('rating-description').text
        
        return [se_rating]

    def _get_school_sf(self, wait):
        tab_sf = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-sf']")))
        tab_sf.click()
        
        xpath_sf = "//div[@class='tab-content print-always']"
        elem_sf = wait.until(EC.presence_of_element_located((By.XPATH, xpath_sf)))
        sf_rating = elem_sf.find_element_by_class_name('rating-description').text
        
        return [sf_rating]

    def _get_school_tr(self, wait):
        tab_tr = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-tr']")))
        tab_tr.click()
        
        xpath_tr = "//div[@class='tab-content print-always']"
        elem_tr = wait.until(EC.presence_of_element_located((By.XPATH, xpath_tr)))
        tr_rating = elem_tr.find_element_by_class_name('rating-description').text
        
        return [tr_rating]

    def _get_school_es(self, wait):
        tab_es = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='tab-button-es']")))
        tab_es.click()
        
        xpath_es = "//div[@class='tab-content print-always']"
        elem_es = wait.until(EC.presence_of_element_located((By.XPATH, xpath_es)))
        es_rating = elem_es.find_element_by_class_name('rating-description').text
        
        return [es_rating]

    def _get_school_data(self, browser, school_name):
        # reset browser to the search box 
        browser.get(CONST.DOE_URL)
        wait = WebDriverWait(browser, 20)
        input_box = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'input')))
        input_box.send_keys(school_name)
        input_clickable = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[@id='result-item-0']")))
        input_clickable.click()
        
        sn = [school_name]
        si = self._get_school_si(wait)
        sa = self._get_school_sa(wait)
        ct = self._get_school_ct(wait)
        se = self._get_school_se(wait)
        es = self._get_school_es(wait)
        sf = self._get_school_sf(wait)
        tr = self._get_school_tr(wait)
        
        data = sn+si+sa+ct+se+es+sf+tr
        
        return data

    def _get_all_schools_data(self, browser, schools):
        schools_data = []
        for school_name in schools:
            data = self._get_school_data(browser, school_name)
            time.sleep(3)
            schools_data.append(data)

        browser.quit()
        return schools_data

    def scrape_school_names(self):
        self._school_names = self._get_schools(self._wait)

    def scrape_school_data(self, school_names):
        self._school_data = self._get_all_schools_data(self._browser, school_names)

    def write_data(self,
                   school_data, 
                   data_path):

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


    @property
    def school_names(self):
        return self._school_names

    @property
    def school_data(self):
        return self._school_data


if __name__ == '__main__':
    chromedriver = '/Users/itachi/Downloads/Chrome/chromedriver'
    data_path = '../data/sample/' 

    doe = nyc_doe(chromedriver)
    doe.scrape_school_names()
    schools_names = doe.school_names

    # divide the school names list into small batches 
    school_batches = np.array_split(schools_names, int(len(schools_names))//10)
    # time of sleep 
    sleep_secs = 15

    # batch jobs start
    print(f'total number of batches: {len(school_batches)}')
    for i, batch in enumerate(school_batches):
        doe.scrape_school_data(batch)
        school_data = doe.school_data
        doe.write_data(school_data, data_path)
        print(f'batch {i} done, sleep {sleep_secs} seconds\n')
        time.sleep(sleep_secs) # rest for a few seconds after each batch job done
    print('job done, congratulations!')
