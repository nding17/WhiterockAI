import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import os

class rent_dot_com:

	def __init__(self, city, state):
		self._city = city
		self._state = state
		self._overhead = 'https://www.rent.com'
		self._apt_urls = []
		self._apt_data = []

	def _get_page_url(self, page_num):
	    city = self._city.lower().replace(' ', '-')
	    state = self._state.lower().replace(' ', '-')
	    page = f'{self._overhead}/{state}/{city}/apartments_condos_houses_townhouses?page={page_num}'
	    return page

	def _get_apt_urls_per_page(self, pg_num):
	    pg_url = self._get_page_url(pg_num)
	    response = requests.get(pg_url)
	    results = response.content
	    apt_urls = []
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	        apts = soup.find_all('div', class_='_3PdAH _1EbNE')
	        for apt in apts:
	            apt_sub = apt.find('div', class_='_3RRl_ _2Hrxl')
	            apt_link = apt_sub.find('a', class_='_3kMwn ByXwK')
	            url = apt_link['href']
	            apt_urls.append(url)
	    
	    return apt_urls

	def _get_apt_urls(self, verbose=False):
	    pg_url = self._get_page_url(1)
	    response = requests.get(pg_url)
	    results = response.content
	    page_num = 0
	    apt_urls = []
	    
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	        apts_num_tag = soup.find('span', class_='_3YJue')
	        apts_num =  apts_num_tag.find('span', 
	                                      attrs={'data-tid':'pagination-total'})\
	                                .get_text()
	        apts_num = int(apts_num)
	        pages_num = int(np.ceil(apts_num/30))
	        if verbose:
	            print(f'total number of apartments in {self._city}, {self._state} is {apts_num}')
	            print(f'total number of pages to be scraped is {pages_num}')
	        
	    for pg_num in range(pages_num):
	        apt_urls += self._get_apt_urls_per_page(pg_num)
	        if verbose:
	            print(f'page {pg_num} done')
	    
	    apt_urls = [url for url in apt_urls if self._state in url]
	    return apt_urls

	def _get_address(self, address_tag, hdr):
		try:
			elements = address_tag.find_all('span')
			address = elements[0].get_text()\
			                     .replace(',','')\
			                     .strip()
			city = elements[1].get_text().strip()
			state = elements[2].get_text().strip()
			zipcode = elements[3].get_text().strip()
			return address, city, state, zipcode
		except:
			address = hdr.get_text()
			elements = address_tag.find_all('span')
			city = elements[0].get_text()\
			                     .replace(',','')\
			                     .strip()
			state = elements[1].get_text().strip()
			zipcode = elements[2].get_text().strip()
			return address, city, state, zipcode

	def _get_units(self, unit_tag):
	    unit = []
	    for cell in unit_tag.find_all('td'):
	        if cell.attrs:
	            if cell['data-tid'] == 'pdpfloorplans-unit-displayText':
	                unit_num = cell.get_text()
	                unit.append(unit_num)
	            if cell['data-tid'] == 'pdpfloorplans-unit-price':
	                try:
	                    unit_price = cell.get_text().replace('$', '')
	                    unit.append(float(unit_price))
	                except:
	                    unit.append(np.nan)
	            if cell['data-tid'] == 'pdpfloorplans-unit-bedbath':
	                try:
	                    bedbath_tag = cell.find_all('span')
	                    bed_tag, bath_tag = bedbath_tag[0], bedbath_tag[1]
	                    pattern = r'[-+]?\d*\.\d+|\d+'
	                    bed = re.findall(pattern, bed_tag.get_text())
	                    bath = re.findall(pattern, bath_tag.get_text())
	                    bed_unit, bath_unit = 0, 0
	                    if bed:
	                        bed_unit = bed[0]
	                    if bath:
	                        bath_unit = bath[0]
	                    unit.append(float(bed_unit))
	                    unit.append(float(bath_unit))
	                except:
	                    unit.append(np.nan)
	                    unit.append(np.nan)
	            if cell['data-tid'] == 'pdpfloorplans-unit-sqft':
	                try:
	                    pattern = r'[-+]?\d*\.\d+|\d+'
	                    sqft_unit = re.findall(pattern, cell.get_text())[0]
	                    unit.append(float(sqft_unit))
	                except:
	                    unit.append(np.nan)
	    return unit

	def _get_floorplan(self, unit_tag):
	    unit = []
	    for cell in unit_tag.find_all('td'):
	        if cell.attrs:
	            if cell['data-tid'] == 'pdpfloorplan-displayText':
	                floorplan_num = cell.get_text()
	                unit.append(floorplan_num)
	            if cell['data-tid'] == 'pdpfloorplan-price':
	                try:
	                    fp_price = cell.get_text()\
	                                   .replace('$','')\
	                                   .replace(',','')
	                    pattern = r'[-+]?\d*\.\d+|\d+'
	                    price = re.findall(pattern, fp_price)[0]
	                    unit.append(float(price))
	                except:
	                    unit.append(np.nan)
	            if cell['data-tid'] == 'pdpfloorplan-bedbaths':
	                try:
	                    bedbath_tag = cell.find_all('span')
	                    bed_tag, bath_tag = bedbath_tag[0], bedbath_tag[1]
	                    pattern = r'[-+]?\d*\.\d+|\d+'
	                    bed = re.findall(pattern, bed_tag.get_text())
	                    bath = re.findall(pattern, bath_tag.get_text())
	                    bed_fp, bath_fp = 0, 0
	                    if bed:
	                        bed_fp = bed[0]
	                    if bath:
	                        bath_fp = bath[0]
	                    unit.append(float(bed_fp))
	                    unit.append(float(bath_fp))
	                except:
	                    unit.append(np.nan)
	                    unit.append(np.nan)
	            if cell['data-tid'] == 'pdpfloorplan-sqft':
	                try:
	                    pattern = r'[-+]?\d*\.\d+|\d+'
	                    sqft_fp = re.findall(pattern, cell.get_text())[0]
	                    unit.append(float(sqft_fp))
	                except:
	                    unit.append(np.nan)
	    return unit

	def _get_apt_info(self, apt_url):

	    complete_url = self._overhead+apt_url
	    response = requests.get(complete_url)
	    results = response.content
	    apt_all = []
	    
	    if not response.status_code == 404:
	        soup = BeautifulSoup(results, 'lxml')
	        address_tag = soup.find('div', '_3wnFl _3wnFl')
	        hdr = soup.find('h1', attrs={'data-tid': 'property-title'})
	        addr = self._get_address(address_tag, hdr)
	        
	        room_tags = soup.find_all('div', '_1ECa-')
	        
	        for rt in room_tags:
	            room_table = rt.find('table', '_1GkPp F4skJ')
	            room_tbody = room_table.find('tbody')
	            floor_plan = room_tbody.find_all('tr')
	            apartments = []
	            for unit_tag in floor_plan:
	                if unit_tag['data-tid'] == 'pdpfloorplan-row':
	                    apt = list(addr)+self._get_floorplan(unit_tag)
	                    apartments.append(apt)

	                if unit_tag['data-tid'] == 'pdpfloorplans-unit-row':
	                    apt = list(addr)+self._get_units(unit_tag)
	                    apartments.append(apt)
	            apt_all += apartments 
	                        
	    return apt_all

	def scrape_apt_urls(self, verbose=False):
		self._apt_urls = self._get_apt_urls(verbose)

	def scrape_apt_data(self, apt_urls, verbose=False):

		apt_all_data = []

		if verbose:
			print(f'aparments in {len(apt_urls)} addresses to be scraped')

		for i, apt_url in enumerate(apt_urls):
			apt_all_data += self._get_apt_info(apt_url)
			if verbose:
				print(f'apartments in address {i} all scraped')

		self._apt_data = apt_all_data

	@property
	def apt_urls(self):
		return self._apt_urls

	@property
	def apt_data(self):
		return self._apt_data

if __name__ == '__main__':

	rdc = rent_dot_com('philadelphia', 'pennsylvania')

	rdc.scrape_apt_urls(verbose=True)
	urls = rdc.apt_urls
	urls_chunk = np.array_split(urls, int(len(urls)//10))

	os.chdir('..')

	if not os.path.exists('data'):
		os.mkdir('data')

	os.chdir('./data')
	if not os.path.exists('sample'):
		os.mkdir('sample')
	os.chdir('sample')

	cols = ['address',
			'city',
			'state',
			'zipcode',
			'apt',
			'price',
			'bedroom',
			'bathroom',
			'sqft']

	if not os.path.exists('rent_dot_com.csv'):
		df = pd.DataFrame([], columns=cols)
		df.to_csv('./rent_dot_com.csv')

	for i, batch_urls in enumerate(urls_chunk[33:]):
		print(batch_urls)
		rdc.scrape_apt_data(batch_urls, verbose=True)
		data = rdc.apt_data
		df_new = pd.DataFrame(data, columns=cols)
		with open('rent_dot_com.csv', 'a') as df_old:
			df_new.to_csv(df_old, header=False)
		print(f'batch {i} finished running')

	print('job finished!')
