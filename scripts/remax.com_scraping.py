#!/usr/bin/env python

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'completed'

import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import os

class remax_dot_com():

	def __init__(self, city, state):
		self._city = city
		self._state = state
		self._overhead = 'https://www.remax.com'
		self._apt_urls = []
		self._apt_data = []

	def _get_webpage(self, pg_num):

		city = self._city.strip().lower()
    	state = self._state.strip().lower()
    	dangle = 'realestatehomesforsale'
    	url = f'{overhead}/{dangle}/{city}-{state}-p{pg_num}.html?query={city},{state}-search/newest-sortorder'
    	return url


   	def _get_apt_urls_per_page(self, pg_num):

   		webpage = get_webpage(pg_num)
    	response = requests.get(webpage)
    	results = response.content
    	apt_urls = []
    
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	        apt_sub_tags = soup.find_all('div', class_='listing-pane-details')
	        
	        for apt_tag in apt_sub_tags:
	            apt_link_tag = apt_tag.find('a', class_='js-detaillink')
	            url = apt_link_tag['href']
	            apt_urls.append(url)
	        
	    return apt_urls

	def _get_ensemble_apt_urls(verbose=False):
	    test_page = get_webpage(1)
	    response = requests.get(test_page)
	    results = response.content
	    apt_ensemble_urls = []
	    
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	        pg_lst = soup.find_all('li', class_='pages-item')
	        try:
	            max_pg_tag = pg_lst[-1].find('a', class_='js-pager-item pages-link')
	            max_pg = int(max_pg_tag.get_text())
	            if verbose:
	                print(f'there are {max_pg} apartment URLs to be collected')
	        except:
	            max_pg = np.nan
	        
	        if not max_pg == np.nan:
	            for pg_num in range(1, max_pg+1):
	                apt_ensemble_urls += get_apt_urls_per_page(pg_num)
	                if verbose:
	                    print(f'page {pg_num} apartment URLs collected')
	        if verbose:
	            print(f'all apartment URLs collected')

	    return apt_ensemble_urls

	def _get_price(self, soup):
	    try:
	        price_tag = soup.find('span', class_='listing-detail-price-amount pad-half-right')
	        price_text = price_tag.get_text()\
	                          .replace(',','')\
	                          .strip()
	        pattern = r'[-+]?\d*\.\d+|\d+'
	        price_unit = re.findall(pattern, price_text)[0]
	        price = float(price_unit)

	        return price
	    except:
	        return np.nan


	def _get_address(self, content_tag):
	    try:
	        address_tag = content_tag.find('div', class_='listing-detail-address')
	        street_tag = address_tag.find('span', attrs={'itemprop': 'streetAddress'})
	        street = street_tag.get_text()\
	                           .strip()\
	                           .replace(',', '')
	        city_tag = address_tag.find('span', attrs={'itemprop': 'addressLocality'})
	        city = city_tag.get_text()\
	                       .strip()\
	                       .replace(',', '')\
	                       .title()
	        state_tag = address_tag.find('span', attrs={'itemprop': 'addressRegion'})
	        state = state_tag.get_text()\
	                         .strip()
	        zipcode_tag = address_tag.find('span', attrs={'itemprop': 'postalCode'})
	        zipcode = zipcode_tag.get_text()\
	                             .strip()
	        
	        return street, city, state, zipcode
	    
	    except:
	        return None, None, None, None

	def _get_sideinfo(self, content_tag):
	    sideinfo = {}
	    try:
	        apt_info_tag = content_tag.find('div', class_='forsalelistingdetail')
	        apt_list_tag = apt_info_tag.find_all('li', class_='listing-detail-stats')
	        
	        for apt_tag in apt_list_tag:
	            spans = apt_tag.find_all('span')
	            key = spans[0].get_text()\
	                          .strip()
	            value = spans[1].get_text()\
	                            .strip()
	            sideinfo[key] = value
	        return sideinfo
	    except:
	        return sideinfo

	def access_dict(self, d, key):
	    try:
	        value = d[key]
	        if 'sqft' in value:
	            value = value.replace(',','')\
	                         .replace('sqft', '')\
	                         .strip()
	        try:
	            return float(value)
	        except: 
	            return value
	    except:
	        return None


	def remax_normal(self, soup):
	    # REMAX normal property
	    content_tag = soup.find('div', class_='property-details-body fullwidth-content-container clearfix')
	    price = get_price(soup)
	    street, city, state, zipcode = get_address(content_tag)
	    sidict = get_sideinfo(content_tag)
	    listid = access_dict(sidict, 'Listing ID')
	    listtype = access_dict(sidict, 'Listing Type')
	    bedrooms = access_dict(sidict, 'Bedrooms')
	    bathrooms = access_dict(sidict, 'Bathrooms')
	    sqft = access_dict(sidict, 'House Size')
	    lotsf = access_dict(sidict, 'Lot Size')
	    waterfront = access_dict(sidict, 'Waterfront')
	    liststatus = access_dict(sidict, 'Listing Status')
	    yrbuilt = access_dict(sidict, 'Year Built')
	    county = access_dict(sidict, 'County')
	    halfbath = access_dict(sidict, 'Half Bath')
	    subdivision = access_dict(sidict, 'Subdivision')
	    cooling = access_dict(sidict, 'Cooling')
	    ac = access_dict(sidict, 'Air Conditioning')
	    appliances = access_dict(sidict, 'Appliances')
	    rooms = access_dict(sidict, 'Rooms')
	    laundry = access_dict(sidict, 'Laundry')
	    taxes = access_dict(sidict, 'Taxes')
	    luxurious = 'No'

	    unit = [
	        street,
	        city,
	        state,
	        zipcode,
	        bathrooms,
	        bedrooms,
	        rooms,
	        waterfront,
	        cooling,
	        ac,
	        appliances,
	        laundry,
	        sqft,
	        price,
	        taxes,
	        listtype,
	        listid,
	        lotsf,
	        liststatus,
	        yrbuilt,
	        county,
	        halfbath,
	        subdivision,
	        luxurious,
	    ]

	    return unit


	def remax_collection(self, soup):
	    # REMAX luxurious property 
	    price = get_price_normal(soup)
	    content_tag = soup.find('div', class_='property-details--details')
	    street, city, state, zipcode = get_address(content_tag)
	    sidict = get_sideinfo(content_tag)
	    listid = access_dict(sidict, 'Listing ID')
	    listtype = access_dict(sidict, 'Listing Type')
	    bedrooms = access_dict(sidict, 'Bedrooms')
	    bathrooms = access_dict(sidict, 'Bathrooms')
	    sqft = access_dict(sidict, 'House Size')
	    lotsf = access_dict(sidict, 'Lot Size')
	    waterfront = access_dict(sidict, 'Waterfront')
	    liststatus = access_dict(sidict, 'Listing Status')
	    yrbuilt = access_dict(sidict, 'Year Built')
	    county = access_dict(sidict, 'County')
	    halfbath = access_dict(sidict, 'Half Bath')
	    subdivision = access_dict(sidict, 'Subdivision')
	    cooling = access_dict(sidict, 'Cooling')
	    ac = access_dict(sidict, 'Air Conditioning')
	    appliances = access_dict(sidict, 'Appliances')
	    rooms = access_dict(sidict, 'Rooms')
	    laundry = access_dict(sidict, 'Laundry')
	    taxes = access_dict(sidict, 'Taxes')
	    luxurious = 'Yes'

	    unit = [
	        street,
	        city,
	        state,
	        zipcode,
	        bathrooms,
	        bedrooms,
	        rooms,
	        waterfront,
	        cooling,
	        ac,
	        appliances,
	        laundry,
	        sqft,
	        price,
	        taxes,
	        listtype,
	        listid,
	        lotsf,
	        liststatus,
	        yrbuilt,
	        county,
	        halfbath,
	        subdivision,
	        luxurious,
	    ]

	    return unit

	def check_lux(self, soup):
	    try:
	        is_lux = False
	        
	        lux_tag = soup.find('span', attrs={
	            'itemprop': 'name',
	            'class': 'js-stateformatted'
	        })
	        
	        lux = lux_tag.get_text()\
	                     .strip()\
	                     .lower()
	        
	        if 'luxury' in lux:
	            is_lux = True
	        return is_lux
	    except:
	        return False

	def get_apt_info(self, apt_url):
	    overhead = 'https://www.remax.com'
	    response = requests.get(overhead+apt_url)
	    results = response.content
	    
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	        is_lux = check_lux(soup)
	        if is_lux:
	            return remax_collection(soup)
	        else:
	            return remax_normal(soup)

