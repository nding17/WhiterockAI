#!/usr/bin/env python

""" 
rent.com_scraping.py : Scrape the apartment rental infomation in rent.com 
all the users need to do is to specify a city and state and it will automatically
scrape all the details related to all the apartments in the city users are
looking at.
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.2'
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
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            apts = soup.find_all('a', attrs={'data-tid': 'property-title'})
            apt_urls = [apt['href'] for apt in apts]

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
            # this is a tag that displays the total number of apartments
            apts_num =  soup.find('span', 
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
        unit_tag : bs4.element.Tag
            a beautifulsoup element tag that contains information about 
            the apartment unit

        Returns
        -------
        unit : list(Object)
            a list that contains information about the apartment unit, 
            including unit number, price, # bedrooms, # bathrooms and
            area measured in square foot 

        >>> _get_units(unit_tag)
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', '0606', 1894.0, 0.0, 1.0, 469.0)

        """

        # a list that contains apartment unit's information
        unit = []
        # use a loop to list all the cells in a row 
        for cell in unit_tag.find_all('td'):
            if cell.attrs: # omit the cell with nothing in it 
                # look for the apartment #, however, this info is not
                # consistent across the entire webiste
                if cell['data-tid'] == 'pdpfloorplans-unit-displayText':
                    unit_num = cell.get_text()
                    unit.append(unit_num)
                # scrape the price of the unit
                if cell['data-tid'] == 'pdpfloorplans-unit-price':
                    try:
                        unit_price = cell.get_text().replace('$', '')
                        # try to convert the price to float 
                        unit.append(float(unit_price))
                    except:
                        # if there's no price for this unit
                        # append the list with a null value 
                        unit.append(np.nan)
                if cell['data-tid'] == 'pdpfloorplans-unit-bedbath':
                    try:
                        # try to extract the tags that include the number
                        # of bedrooms and bathrooms 
                        bedbath_tag = cell.find_all('span')
                        bed_tag, bath_tag = bedbath_tag[0], bedbath_tag[1]
                        # regular expression pattern for extracting any types
                        # of numbers, including integer and floating numbers 
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
                        # if the convertion failed, append the list
                        # will two null values 
                        unit.append(np.nan)
                        unit.append(np.nan)
                if cell['data-tid'] == 'pdpfloorplans-unit-sqft':
                    # follow the same procedure as above, but this time
                    # scrape the square foot of the apartment unit
                    try:
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        sqft_unit = re.findall(pattern, cell.get_text())[0]
                        unit.append(float(sqft_unit))
                    except:
                        unit.append(np.nan)
        return unit

    def _get_floorplan(self, unit_tag):
        """
        Scrape the actual apartments' information in the table provided by 
        a specific address

        -------

        very similar to the code in _get_units(unit_tag) function, this functino
        aims to scrape the apartment unit's info in the white background if you
        open the webpage. It's usually a summary of a list of apartments. 

        Parameters
        ----------
        unit_tag : bs4.element.Tag
            a beautifulsoup element tag that contains information about 
            the apartment unit

        Returns
        -------
        unit : list(Object)
            a list that contains information about the apartment unit, 
            including unit number, price, # bedrooms, # bathrooms and
            area measured in square foot 

        >>> _get_units(unit_tag)
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', 'Studio-S4B', '0606', 1894.0, 0.0, 1.0, 469.0)

        """
        unit = []
        for cell in unit_tag.find_all('td'):
            if cell.attrs:
                # scrape the apartment number 
                if cell['data-tid'] == 'pdpfloorplan-displayText':
                    floorplan_num = cell.get_text()
                    unit.append(floorplan_num)
                # scrape the apartment price 
                if cell['data-tid'] == 'pdpfloorplan-price':
                    try:
                        # remove any punctuation marks and $ sign
                        fp_price = cell.get_text()\
                                       .replace('$','')\
                                       .replace(',','')
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        price = re.findall(pattern, fp_price)[0]
                        unit.append(float(price))
                    except:
                        unit.append(np.nan)
                # scrape the number of bedrooms and bathrooms 
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
                # scrape the area of the apartment in square foot 
                if cell['data-tid'] == 'pdpfloorplan-sqft':
                    try:
                        pattern = r'[-+]?\d*\.\d+|\d+'
                        sqft_fp = re.findall(pattern, cell.get_text())[0]
                        unit.append(float(sqft_fp))
                    except:
                        unit.append(np.nan)
        return unit

    def _get_apt_info(self, apt_url):
        """
        Given the apartment URL, scrape the apartment unit's information regardless
        of what type of tag it is

        -------
        
        Systematically run through the entire webpage of the apartments located in a 
        fixed address, and scrape all the relevant information that's out there in the page.
        That being said, studio apartments, 1bed, 2beds etc. 

        Parameters
        ----------
        apt_url : str
            a specific apartment URL that has a fixed physical address

        Returns
        -------
        apt_all : list(Object) 
            a list of apartment information

        >>> _get_apt_info(apt_url)
        [('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', 'Studio-S4B', 1894.0, 0.0, 1.0, 469.0),
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', '0903', 1894.0, 0.0, 1.0, 469.0),
        ('1520 Hamilton Street', 'Philadelphia', 'Pennsylvania', '19130', '1003', 1894.0, 0.0, 1.0, 469.0),
        ....]
        """

        # get the complete url of the apartments in a specified address 
        complete_url = self._overhead+apt_url
        response = requests.get(complete_url)
        results = response.content
        # a list that contains all the apartment information
        apt_all = []
        
        if not response.status_code == 404:
            try:
                soup = BeautifulSoup(results, 'lxml')
                # address tag
                address_tag = soup.find('div', attrs={'data-tid': 'pdpKeyInfo_address'})
                # header tag
                hdr = soup.find('h1', attrs={'data-tid': 'property-title'})
                # scrape the address information
                # get a tuple
                addr = self._get_address(address_tag, hdr)
                # a list of room tags, this might need to be constantly updated
                room_tags = soup.find_all('div', '_21XBf')
            except:
                return apt_all

            for rt in room_tags:
                # for each room tag, identify what type of rows the room tag is
                # only two options: unit in grey background, floorplan in white
                # background 
                room_table = rt.find('table', attrs={'data-tid': 'pdpfloorplan-table'})
                room_tbody = room_table.find('tbody')
                floor_plan = room_tbody.find_all('tr')
                apartments = []
                for unit_tag in floor_plan:
                    # unit tag
                    if unit_tag['data-tid'] == 'pdpfloorplan-row':
                        apt = list(addr)+self._get_floorplan(unit_tag)
                        apartments.append(apt)
                    # floorplan tag
                    if unit_tag['data-tid'] == 'pdpfloorplans-unit-row':
                        apt = list(addr)+self._get_units(unit_tag)
                        apartments.append(apt)
                # update the list that contains all the apartments info
                apt_all += apartments 
                            
        return apt_all

    def scrape_apt_urls(self, verbose=False):
        """
        A public function that allows you to call to scrape apartment URLs

        Parameters
        ----------
        verbose : boolean
            a flag you can enable to see the scraping progress

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_urls will be updated
            and all the apartments URLs will be stored in this field 
        """
        self._apt_urls = self._get_apt_urls(verbose)

    def scrape_apt_data(self, apt_urls, verbose=False):
        """
        A public function that allows you to call to scrape apartment information

        Parameters
        ----------
        apt_urls : list(str)
            a list of apartment URLs that you hope to scrape the apartment 
            info from

        verbose : boolean
            a flag you can enable to see the scraping progress

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_data will be updated
            and all the apartments info will be stored in this field 
        """

        apt_all_data = []

        if verbose:
            print(f'aparments in {len(apt_urls)} addresses to be scraped')

        # loop through all the apartment URLs and scrape all the apartments
        # information in each URL
        for i, apt_url in enumerate(apt_urls):
            apt_all_data += self._get_apt_info(apt_url)
            if verbose:
                print(f'apartments in address {i} all scraped')

        self._apt_data = apt_all_data

    @property
    def apt_urls(self):
        # serve as a way to show the apt_urls
        return self._apt_urls

    @property
    def apt_data(self):
        # serve as a way to show the apt_data
        return self._apt_data

if __name__ == '__main__':
    # construct data scraping object, use Philadelphia, Pennsylvania 
    # as an example
    rdc = rent_dot_com('philadelphia', 'pennsylvania')

    # scrape all the apartment URLs in Philadelphia
    # status update enabled
    rdc.scrape_apt_urls(verbose=True)
    urls = rdc.apt_urls
    # in order to avoid crashes and loses all your data
    # divide the list of URLs in batches and keep updating
    # the csv file once the batch job is finished
    urls_chunk = np.array_split(urls, int(len(urls)//10))

    # try to see if the current directory has a folder 
    # that you can use to store data 
    os.chdir('..')

    # this could be modified to fit the structure of 
    # a specific user's directory
    if not os.path.exists('data'):
        os.mkdir('data')

    os.chdir('./data')
    if not os.path.exists('sample'):
        os.mkdir('sample')
    os.chdir('sample')

    # the column names of the data frame 
    cols = ['address',
            'city',
            'state',
            'zipcode',
            'apt',
            'price',
            'bedroom',
            'bathroom',
            'sqft']

    # create an initial empty data file with all 
    # the features of an apartment 
    if not os.path.exists('rent_dot_com.csv'):
        df = pd.DataFrame([], columns=cols)
        df.to_csv('./rent_dot_com.csv')

    # running the batch and keep saving the intermediary 
    # results from the data scraping jobs 
    # each batch contains 10 URLs, but this could be modified
    for i, batch_urls in enumerate(urls_chunk):
        # print(batch_urls)
        rdc.scrape_apt_data(batch_urls, verbose=True)
        data = rdc.apt_data
        df_new = pd.DataFrame(data, columns=cols)
        # append the results from each batch
        with open('rent_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)
        print(f'batch {i} finished running')

    print('job finished!')
