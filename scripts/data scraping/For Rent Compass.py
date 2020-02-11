__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.2'
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
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class compass_dot_com:

	def __init__(self, city, state):
		self._city = city
		self._state = state

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


if __name__ == '__main__':
	codc = compass_dot_com('new york', 'ny')
	codc._get_browser('https://www.compass.com/for-rent/new-york-ny/')