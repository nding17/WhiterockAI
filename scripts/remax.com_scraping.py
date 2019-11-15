#!/usr/bin/env python

""" 
remax.com_scraping.py : Scrape the apartment rental infomation in remax.com 
all the users need to do is to specify a city and state (abbreivated) and 
it will automatically scrape all the details related to all the apartments 
in the city users are looking at.
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'completed'

### packages need to be imported 
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import os

class remax_dot_com:

    # initialization - users need to specify a city and state 
    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._overhead = 'https://www.remax.com'
        self._apt_urls = []
        self._apt_data = []

    def _get_webpage(self, pg_num):

        """
        Get the page link with a specific page.
        
        Parameters
        ----------
        pg_num : int
            page number of the apartments in a specific city

        Returns
        -------
        string 
            the link of the page, given the page number 

        >>> _get_webpage(1)
        'remax.com/realestatehomesforsale/philadelphia-pa-p001.html?query=philadelphia,pa-search/newest-sortorder'

        """

        # for city comes with 2 words, replace the space with -
        # e.g. 'new york' -> 'new-york'
        city = self._city.strip().lower().replace(' ', '-')
        state = self._state.strip().lower().replace(' ', '-')
        # after the overhead, there's a dangle attached with the 
        # URL of this website 
        dangle = 'realestatehomesforsale'
        overhead = self._overhead
        url = f'{overhead}/{dangle}/{city}-{state}-p{pg_num}.html?query={city},{state}-search/newest-sortorder'
        return url


    def _get_apt_urls_per_page(self, pg_num):

        """
        Get all the apartment URLs listed in the same page (24 URLs per page)

        Parameters
        ----------
        pg_num : int
            page number of the apartments in a specific city

        Returns:
        apt_urls : list(str)
            a list of apartment URLs correspond to different apartments in 
            a same page 

        """

        # fetch the URL of the webpage given the page number
        webpage = self._get_webpage(pg_num)
        # send a request to get the HTML content of that page 
        response = requests.get(webpage)
        results = response.content
        apt_urls = [] # apartment URLs to be stored 
    
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            # locate the tag that contains the bulk of the apartment contents
            apt_sub_tags = soup.find_all('div', class_='listing-pane-details')
            
            # extract the link to each apartment from all the apartment tags 
            for apt_tag in apt_sub_tags:
                apt_link_tag = apt_tag.find('a', class_='js-detaillink')
                url = apt_link_tag['href'] # extract the apartment URL
                apt_urls.append(url)
            
        return apt_urls

    def _get_ensemble_apt_urls(self, verbose=False, test=False):

        """
        Get all the relevant apartment links in remax.com with a specified city

        Parameters
        ----------
        verbose : boolean (optional)
            since the scraping process takes quite a while, you have the option
            to monitor the progress by enabling the status updates

        test : boolean (optional)
            this could be turned on for testing and debugging purposes. When it's
            turned on, only 50 pages' apartment URLs will be scraped so you have 
            faster runtime

        Returns
        -------
        apt_urls : list(str)
            a list of apartment URLs corresponding to different apartments in 
            a same page

        """

        test_page = self._get_webpage(1)
        response = requests.get(test_page)
        results = response.content
        apt_ensemble_urls = []
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            pg_lst = soup.find_all('li', class_='pages-item')
            try:
                pg_tags = [pg.find('a', class_='js-pager-item pages-link') for pg in pg_lst]
                pg_nums = []
                for pg_tag in pg_tags:
                    if pg_tag:
                        try:
                            pg_nums.append(int(pg_tag.get_text()))
                        except:
                            continue
                max_pg = max(pg_nums)

                if test:
                    max_pg = 50

                if verbose:
                    print(f'there are {max_pg} apartment URLs to be collected')
            except:
                max_pg = np.nan
            
            if not max_pg == np.nan:
                for pg_num in range(1, max_pg+1):
                    apt_ensemble_urls += self._get_apt_urls_per_page(pg_num)
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

    def _access_dict(self, d, key):
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


    def _remax_apt(self, soup, content_tag):
        price = self._get_price(soup)
        street, city, state, zipcode = self._get_address(content_tag)
        sidict = self._get_sideinfo(content_tag)
        listid = self._access_dict(sidict, 'Listing ID')
        listtype = self._access_dict(sidict, 'Listing Type')
        bedrooms = self._access_dict(sidict, 'Bedrooms')
        bathrooms = self._access_dict(sidict, 'Bathrooms')
        interior = self._access_dict(sidict, 'Interior Features')
        sqft = self._access_dict(sidict, 'House Size')
        lotsf = self._access_dict(sidict, 'Lot Size')
        waterfront = self._access_dict(sidict, 'Waterfront')
        liststatus = self._access_dict(sidict, 'Listing Status')
        yrbuilt = self._access_dict(sidict, 'Year Built')
        county = self._access_dict(sidict, 'County')
        school = self._access_dict(sidict, 'County School District')
        halfbath = self._access_dict(sidict, 'Half Bath')
        subdivision = self._access_dict(sidict, 'Subdivision')
        cooling = self._access_dict(sidict, 'Cooling')
        heating = self._access_dict(sidict, 'Heating')
        ac = self._access_dict(sidict, 'Air Conditioning')
        appliances = self._access_dict(sidict, 'Appliances')
        rooms = self._access_dict(sidict, 'Rooms')
        laundry = self._access_dict(sidict, 'Laundry')
        taxes = self._access_dict(sidict, 'Taxes')
        yrtax = self._access_dict(sidict, 'TaxYear')
        possession = self._access_dict(sidict, 'Possession')

        unit = [
            street,
            city,
            state,
            zipcode,
            bathrooms,
            bedrooms,
            interior,
            rooms,
            cooling,
            heating,
            ac,
            appliances,
            laundry,
            sqft,
            price,
            taxes,
            yrtax,
            listtype,
            listid,
            possession,
            lotsf,
            liststatus,
            yrbuilt,
            county,
            school,
            halfbath,
            subdivision,
        ]

        return unit

    def _check_lux(self, soup):
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

    def _get_apt_info(self, apt_url):
        response = requests.get(self._overhead+apt_url)
        results = response.content
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            is_lux = self._check_lux(soup)
            lux = 'No'
            if is_lux:
                content_tag = soup.find('div', class_='property-details--details')
                lux = 'Yes'
            else:
                content_tag = soup.find('div', class_='property-details-body fullwidth-content-container clearfix')
            
            apt_info = self._remax_apt(soup, content_tag)
            apt_info.append(lux)

        return apt_info

    def scrape_apt_urls(self, verbose=False, test=False):
        self._apt_urls = self._get_ensemble_apt_urls(verbose=verbose, test=test)

    def scrape_apt_data(self, apt_urls, verbose=False):
        apt_all_data = []

        if verbose:
            print(f'{len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            apt_all_data.append(self._get_apt_info(apt_url)) 
        
        self._apt_data = apt_all_data

    @property
    def apt_urls(self):
        return self._apt_urls
    
    @property
    def apt_data(self):
        return self._apt_data
    
if __name__ == '__main__':

    rmdc = remax_dot_com('philadelphia', 'pa')

    rmdc.scrape_apt_urls(verbose=True)
    urls = rmdc.apt_urls

    urls_chuck = np.array_split(urls, int(len(urls))//20)

    os.chdir('..')

    if not os.path.exists('data'):
        os.mkdir('data')

    os.chdir('./data')
    if not os.path.exists('sample'):
        os.mkdir('sample')
    os.chdir('sample')

    cols = [
        'address',
        'city',
        'state',
        'zipcode',
        'bathrooms',
        'bedrooms',
        'interior_features',
        'rooms',
        'cooling',
        'heating',
        'AC',
        'appliances',
        'laundry',
        'sqft',
        'price',
        'taxes',
        'tax_year',
        'list_type',
        'list_id',
        'possession',
        'lot_sqft',
        'list_status',
        'year_built',
        'county',
        'county_school_district',
        'half_bath',
        'subdivision',
        'luxury_home',
    ]

    if not os.path.exists('remax_dot_com.csv'):
        df = pd.DataFrame([], columns=cols)
        df.to_csv('./remax_dot_com.csv')

    print(f'batch jobs started, {len(urls_chuck)} batches in total')

    for i, batch_urls in enumerate(urls_chuck):
        rmdc.scrape_apt_data(batch_urls, verbose=True)
        data = rmdc.apt_data
        df_new = pd.DataFrame(data, columns=cols)

        with open('remax_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)
        print(f'batch {i} finished running')

    print('job done!')
