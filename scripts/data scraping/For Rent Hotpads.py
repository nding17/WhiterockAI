__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
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

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
from fake_useragent import UserAgent
from os import listdir
from os.path import isfile, join


class hotpads_dot_com:

    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._browser, _ = self._get_browser(f'https://hotpads.com/{self._city}-{self._state}/apartments-for-rent')

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
        browser = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        browser.get(webpage)
        wait = WebDriverWait(browser, 20) # maximum wait time is 20 seconds 
        return browser, wait

if __name__ == '__main__':
    hdc = hotpads_dot_com('philadelphia', 'pa')