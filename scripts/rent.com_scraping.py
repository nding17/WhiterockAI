#!/usr/bin/env python

""" 
rent.com_scraping.py : Scrape the apartment rental infomation in rent.com 
all the users need to do is to specify a city and state and it will automatically
scrape all the details related to all the apartments in the city you are looking
at.
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__status__ = 'completed'

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
        """
        Get the page link with a specific page.
        
        Parameters
        ----------
        page_num : int
            page number of the apartments in a specific city

        Returns
        -------
        string 
            the link of the page, given the page number 

        >>> _get_page_url(1)
        'rent.com/pennsylvania/philadelphia/apartments_condos_houses_townhouses?page=1'

        """

        # for city comes with 2 words, replace the space with -
        # e.g. 'new york' -> 'new-york'
        city = self._city.lower().replace(' ', '-')
        state = self._state.lower().replace(' ', '-')
        page = f'{self._overhead}/{state}/{city}/apartments_condos_houses_townhouses?page={page_num}'
        return page

    def _get_apt_urls_per_page(self, pg_num):
        """
        Get all the apartment URLs listed in the same page (30 URLs per page)

        Parameters
        ----------
        pg_num : int
            page number of the apartments in a specific city

        Returns:
        apt_urls : list(str)
            a list of apartment URLs correspond to different apartments in 
            a same page 

        """

        # get the URL for the specific page given its page number 
        pg_url = self._get_page_url(pg_num)
        response = requests.get(pg_url)
        # scrape the HTML web content from rent.com
        results = response.content 
        # a list that contains all the apartment URLs
        apt_urls = []
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            # apartment tags
            apts = soup.find_all('div', class_='_3PdAH _1EbNE')
            for apt in apts:
                apt_sub = apt.find('div', class_='_3RRl_ _2Hrxl')
                # find the URL tag
                apt_link = apt_sub.find('a', class_='_3kMwn ByXwK')
                url = apt_link['href']
                apt_urls.append(url)
        
        return apt_urls

    def _get_apt_urls(self, verbose=False):
        """
        Get all the relevant apartment links in rent.com with a specified city

        Parameters
        ----------
        verbose : boolean (optional)
            since the scraping process takes quite a while, you have the option
            to monitor the progress by enabling the status updates 

        Returns
        -------
        apt_urls : list(str)
            a list of apartment URLs correspond to different apartments in 
            a same page

        """

        # access the first page and navigate through the page to check the total
        # number of apartments
        pg_url = self._get_page_url(1)
        response = requests.get(pg_url)
        results = response.content
        page_num = 0
        apt_urls = []
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            apts_num_tag = soup.find('span', class_='_3YJue')
            # this is a tag that displays the total number of apartments
            apts_num =  apts_num_tag.find('span', 
                                          attrs={'data-tid':'pagination-total'})\
                                    .get_text()
            # try to convert text into integer 
            apts_num = int(apts_num)
            # since every page contains 30 apartments, divide the total number of 
            # apartments by 30 will give you the total number of pages
            pages_num = int(np.ceil(apts_num/30))
            # if enabled, you will see status updates on the terminal
            if verbose:
                print(f'total number of apartments in {self._city}, {self._state} is {apts_num}')
                print(f'total number of pages to be scraped is {pages_num}')
        
        # after getting the total number of pages that need to be scraped,
        # we can leave the rest for the loop to handle 
        for pg_num in range(pages_num):
            apt_urls += self._get_apt_urls_per_page(pg_num)
            if verbose:
                print(f'page {pg_num} done')
        
        # make sure that all the links are in the state user specified 
        apt_urls = [url for url in apt_urls if self._state in url]
        return apt_urls

    def _get_address(self, address_tag, hdr):
        """
        Scrape the address of the apartment given the address HTML tag

        Parameters
        ----------
        address_tag : bs4.element.Tag
            a beautifulsoup element tag containing address information
            of the apartment

        hdr : bs4.element.Tag
            a beautifulsoup element tag containing header information of
            the apartment in case there's no address in the address section
            of the webpage 

        Returns
        -------
        (address, city, state, zipcode) : tuple(str)

        >>> _get_address(address_tag, hdr)
        ('1015 S 18th St', 'Philadelphia', 'Pennsylvania', '19146')

        """

        # try to find all the span tags in the address tag, the span tags
        # include all the address information we need 
        try:
            elements = address_tag.find_all('span')

            # scrape the text out of the span tags and remove
            # all the whitespaces and punctuation marks
            address = elements[0].get_text()\
                                 .replace(',','')\
                                 .strip()
            city = elements[1].get_text().strip()
            state = elements[2].get_text().strip()
            zipcode = elements[3].get_text().strip()
            return address, city, state, zipcode
        # however, sometimes the address tag does not include the street
        # info, in this case, use the text in the header tag, which serves
        # as a replacement for the address 
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
        """
        Scrape the actual apartments' information in the table provided by 
        a specific address

        -------

        When you open up the apartment page, this should be the units with 
        grey backgroud, rather than the rows in bright white background

        Parameters
        ----------



        """
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
            try:
                soup = BeautifulSoup(results, 'lxml')
                address_tag = soup.find('div', '_3wnFl _3wnFl')
                hdr = soup.find('h1', attrs={'data-tid': 'property-title'})
                addr = self._get_address(address_tag, hdr)
                
                room_tags = soup.find_all('div', '_1ECa-')
            except:
                return apt_all

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

    for i, batch_urls in enumerate(urls_chunk):
        # print(batch_urls)
        rdc.scrape_apt_data(batch_urls, verbose=True)
        data = rdc.apt_data
        df_new = pd.DataFrame(data, columns=cols)
        with open('rent_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)
        print(f'batch {i} finished running')

    print('job finished!')
