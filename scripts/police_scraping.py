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
		self._browser, self._wait = self._get_browser()


	def _random_user_agent():
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

	def _get_soup(url):
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
	    headers = {'User-Agent': _random_user_agent()}
	    # send a request and get the soup
	    response = requests.get(url, headers=headers)
	    results = response.content
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	    return soup

	def _soup_attempts(url, total_attempts=5):

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

	    soup = _get_soup(url)

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

	def _get_browser():
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
	    options = _build_chrome_options()

	    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=options)
	    browser.get(police_url)
	    wait = WebDriverWait(browser, 10) # maximum wait time is 20 seconds 
	    return browser, wait