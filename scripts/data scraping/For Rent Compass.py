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
from fake_useragent import UserAgent
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

class compass_dot_com:

	def __init__(self, city, state):
		self._city = city.lower().replace(' ', '-')
		self._state = state.lower()
		self._url = f'https://www.compass.com/for-rent/{self._city}-{self._state}/'
		self._browser = self._get_browser(self._url)

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

	def _get_apt_urls(self):
		apt_urls = []
		browser = self._browser
		try:
			while True:
				atags = browser.find_elements_by_xpath("//a[@class='uc-listingPhotoCard uc-listingCard uc-listingCard-has-photo']")
				hrefs = [atag.get_attribute('href') for atag in atags]
				apt_urls += hrefs
				button = browser.find_element_by_xpath("//button[@data-tn='arrowButtonRight']")
				button.click() # click until the last possible right arrow 
		except:
			# if the last page is reached then we can return all the apartment urls that link to the 
			# apartments 
			return apt_urls

	def _get_address(self, soup):
		address = soup.find('p', attrs={'data-tn': 'listing-page-address'}) \
					  .get_text()
		if 'unit' in address.lower():
			addr_lst = address.split(',')
			addr = addr_lst[0].strip()
			unit = addr_lst[1].strip()
		else:
			addr = address.strip()
			unit = None

		zipcode = soup.find('div', attrs={'data-tn': 'listing-page-address-subtitle'}) \
					  .get_text() \
					  .split(',')[-1] \
					  .strip() \
					  .split(' ')[-1] \
					  .strip()

		return addr, unit, zipcode

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

	def _get_price(self, soup):
		price_tags = soup.find('div', class_='u-flexContainer--row summary__RightContent-e4c4ok-4 eFqMfB') \
						 .find_all('div', class_='summary__StyledSummaryDetailUnit-e4c4ok-13 bgfBKu')

		keys = [tag.find('div', class_='textIntent-caption2 summary__SummaryCaption-e4c4ok-5 bcaMfK').get_text() for tag in price_tags]
		values = [self._parse_num(tag.find('div', class_='textIntent-title2').get_text()) for tag in price_tags]

		d = dict(zip(keys, values))
		return d['Price'], d['Beds'], d['Bath']

	def _get_sf(self, soup):
		sqft = soup.find('div', attrs={'data-tn': 'listing-page-summary-sq-ft'}) \
				   .find('div', class_='textIntent-title2') \
				   .get_text()
		sqft = self._parse_num(sqft)
		return sqft

	def _get_apt_data(self, url):
		soup = self._get_soup(url)
		addr, unit, zipcode = self._get_address(soup)
		price, beds, bath = self._get_price(soup)
		sqft = self._get_sf(soup)
		return addr, unit, zipcode, price, beds, bath, sqft

if __name__ == '__main__':
	codc = compass_dot_com('new york', 'ny')
	print(codc._get_apt_data('https://www.compass.com/listing/1329-fulton-street-unit-store-brooklyn-ny-11216/426326699769857857/?origin_type=Listing%20Photocard&result_id=bf2ce9ab-fe94-4d8e-9e96-547e89c55f99'))


