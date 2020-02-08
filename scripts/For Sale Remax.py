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
__version__ = '1.0.2'
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

        (private function)
        
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

        (private function)

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

        (private function)

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

        # at the bottom of every page, there are buttons to let you choose 
        # which page you want to go, including the last page of the apartments
        # in this city. We can use it to figure out the max number of pages 
        test_page = self._get_webpage(1)
        response = requests.get(test_page)
        results = response.content
        # all the apartment URLs go here 
        apt_ensemble_urls = [] 
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            pg_lst = soup.find_all('li', class_='pages-item')
            try:
                # extract all the tags related to page number 
                pg_tags = [pg.find('a', class_='js-pager-item pages-link') for pg in pg_lst]
                pg_nums = []
                for pg_tag in pg_tags:
                    if pg_tag:
                        try:
                            # try to extract all the page number
                            pg_nums.append(int(pg_tag.get_text()))
                        except:
                            continue
                # find the maximun page number so we know exactly how 
                # many pages needed to be scraped 
                max_pg = max(pg_nums)

                # if the test flag is enabled, we use 50 pages 
                # to reduce runtime 
                if test:
                    max_pg = 50

                if verbose:
                    print(f'there are {max_pg} apartment URLs to be collected')
            except:
                # failed to find max number of webpages 
                max_pg = np.nan
            
            if not max_pg == np.nan:
                for pg_num in range(1, max_pg+1):
                    # use an iterative method to scrape all the apartment 
                    # URLs in every single page
                    apt_ensemble_urls += self._get_apt_urls_per_page(pg_num)
                    if verbose:
                        print(f'page {pg_num} apartment URLs collected')
    
            if verbose:
                print(f'all apartment URLs collected')

        return apt_ensemble_urls

    def _get_price(self, soup):

        """
        Scrape the price of the apartment given the BeautifulSoup scraper 

        (private function)

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a BeautifulSoup scraper object that contains all the elements 
            in a webpage

        Returns
        -------
        price : float
            the price of the apartment (sell price, not rental price)

        >>> _get_price(soup)
        114000.0

        """

        try:
            # try to locate the price tag 
            price_tag = soup.find('span', class_='listing-detail-price-amount pad-half-right')
            # remove punctuation marks 
            price_text = price_tag.get_text()\
                              .replace(',','')\
                              .strip()

            # extract the numerical price value 
            pattern = r'[-+]?\d*\.\d+|\d+'
            price_unit = re.findall(pattern, price_text)[0]

            # convert the price to float 
            price = float(price_unit)
            return price

        except:
            return np.nan


    def _get_address(self, content_tag):

        """
        Scrape the address of the apartment given the content tag of 
        the specific apartment page 

        (private function)

        Parameters
        ----------
        content_tag : bs4.element.Tag
            a beautifulsoup element tag containing the content information
            of the apartment, including address, bedrooms, area etc. 

        Returns
        -------
        (street, city, state, zipcode) : tuple(str)

        >>> _get_address(content_tag)
        ('767 N 24TH ST', 'Philadelphia', 'PA', '19130')

        """

        try:
            # from the content tag, extract the tag that contains all the address info
            address_tag = content_tag.find('div', class_='listing-detail-address')
            # street tag
            street_tag = address_tag.find('span', attrs={'itemprop': 'streetAddress'})
            # street information
            street = street_tag.get_text()\
                               .strip()\
                               .replace(',', '')
            # city tag       
            city_tag = address_tag.find('span', attrs={'itemprop': 'addressLocality'})
            # city information
            city = city_tag.get_text()\
                           .strip()\
                           .replace(',', '')\
                           .title()
            # state tag
            state_tag = address_tag.find('span', attrs={'itemprop': 'addressRegion'})
            # state information
            state = state_tag.get_text()\
                             .strip()
            # zipcode tag
            zipcode_tag = address_tag.find('span', attrs={'itemprop': 'postalCode'})
            # zipcode information
            zipcode = zipcode_tag.get_text()\
                                 .strip()
            
            return street, city, state, zipcode
        
        except:
            # return None if any of the above parts failed
            # if there's any part that's missing in the address part,
            # the whole address becomes useless
            return None, None, None, None

    def _get_sideinfo(self, content_tag):

        """
        Scrape all the important information of the apartment given the 
        content tag of the specific apartment page 

        (private function)

        -------

        After inspection of the webpage, I find out that there are some 
        features some apartments have, but others don't have. Therefore,
        it would not be feasible if we want to store all the information 
        in a structured database. 

        Therefore, I tried my best to pick the common features almost 
        every apartment should have (list type, bathrooms, bedrooms ...) 
        and some unique and important features that might be missing 
        for a lot of other apartments 

        The best way to store all these unstructed information thus 
        comes to use a dictionary 

        Parameters
        ----------
        content_tag : bs4.element.Tag
            a beautifulsoup element tag containing the content information
            of the apartment, including address, bedrooms, area etc. 

        Returns
        -------
        sideinfo : dict
            a dictionary that contains all the information that an apartment 
            could have included in the webpage 

        >>> _get_sideinfo(content_tag)

        {'Listing Type': 'Condo/Townhome', 
        'Listing ID': 'PAPH848950', 
        'House Size': '2,159 sqft', 
        'Lot Size': '1,742.00 sqft'}

        """

        # dictionary that used to store all the relevant information
        # regarding an apartment
        sideinfo = {} 
        try:
            # main content of all the relavent features 
            apt_info_tag = content_tag.find('div', class_='forsalelistingdetail')
            # extract the contents as lists
            apt_list_tag = apt_info_tag.find_all('li', class_='listing-detail-stats')
            
            for apt_tag in apt_list_tag:
                spans = apt_tag.find_all('span')
                # construct (key, value) pair for the dictionary 
                key = spans[0].get_text()\
                              .strip()
                value = spans[1].get_text()\
                                .strip()
                # fill in the dictionary
                sideinfo[key] = value
            return sideinfo
        except:
            return sideinfo

    def _access_dict(self, d, key):
        """
        Access the dictionary with a known or unknown key without 
        breaking the program using defensive programming

        Parameters
        ----------
        d : dict
            a dictionary that contains all the features information
            of an apartment using _get_sideinfo() function

        key : str
            the key that the users want to extract the value from 
            the dictionary from  

        Returns
        -------
        value : str or float
            the function will try to identify any numerical value 
            and convert it to float. If it's supposed to be a string,
            it will leave it as it is 

        >>> _access_dict('Listing Type')
        'Condo/Townhome'

        >>> _access_dict('Lot Size')
        1742.00

        >>> _access_dict('Listing ID')
        'PAPH848950'

        """
        try:
            # try to get access to the value by using the key
            value = d[key]
            if 'sqft' in value:
                # try to format any area related features 
                # remove punctuation marks and text
                value = value.replace(',','')\
                             .replace('sqft', '')\
                             .strip()
            try:
                # try to convert any numerical type features 
                # into float 
                return float(value)
            except: 
                # if this is a text value, leave it as it is 
                return value
        except:
            # fail to access the value from the key
            # namely, the feature does not exist in the 
            # feature dictionary of a specific apartment
            return None


    def _remax_apt(self, soup, content_tag):

        """
        Scrape all the relavent information of the apartment given 
        the content tag of the specific apartment page and standardize
        them into a structured format 

        (private function)

        Parameters
        ----------
        content_tag : bs4.element.Tag
            a beautifulsoup element tag containing the content information
            of the apartment, including address, bedrooms, area etc. 

        Returns
        -------
        list(Object)
            list that contains features information about an apartment 

        >>> _remax_apt(soup, content_tag)
        ['767 N 24TH ST', 'Philadelphia', 'PA', '19130', ... , 'Philadelphia', None, 'Fairmount']

        """

        # as dicussed earlier, the best format to store all the information
        # is by creating dictionaries to store the unstructured information
        # but here are the features that are common across all aparments and 
        # I also picked some features I think are important
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

        # package all the features into a list 
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

        """
        Check the type of the apartment based on the webpage

        (privare funtion)

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a BeautifulSoup scraper object that contains all the elements 
            in a webpage

        Returns
        -------
        is_lux : Boolean

        >>> _check_lux(soup)
        False

        """
        try:
            is_lux = False
            
            # if this is a collection apartment
            # it would have a tag indicating 'luxury home'
            lux_tag = soup.find('span', attrs={
                'itemprop': 'name',
                'class': 'js-stateformatted'
            })
            
            # strip the text out of this tag
            lux = lux_tag.get_text()\
                         .strip()\
                         .lower()
            
            # check keyword 'luxury'
            if 'luxury' in lux:
                is_lux = True
            return is_lux
        except:
            return False

    def _get_apt_info(self, apt_url):

        """
        Given the apartment URL, scrape the apartment unit's information regardless
        of what type of apartment it is. 

        (private function)

        -------
        
        In this website, we have two types of apartment, namely, normal apartments 
        and collection apartments. Normal apartments have a bright blue background 
        which forms the majority the apartments in this website. 

        Collection apartments are luxurious type apartments that have their own 
        specially designed webpages to differentiate from the normal apartment 
        webpages (dark navy background). We need to identify  these two different 
        types of apartments and handle them differently.   

        Parameters
        ----------
        apt_url : str
            a specific apartment URL that has a fixed physical address

        Returns
        -------
        apt_all : list(list(Object)) 
            a list of apartment information

        >>> _get_apt_info(apt_url)
        [['767 N 24TH ST', 'Philadelphia', 'PA', '19130', ... , 'Philadelphia', None, 'Fairmount', 'Yes'],
         ['1417 N 8TH ST', 'Philadelphia', 'PA', '19122', ... , 'Philadelphia County', None, 'Ludlow', 'Yes']
         ...]
        """

        response = requests.get(self._overhead+apt_url)
        results = response.content
        
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
            # check what type of apartment this is - normal or collection
            is_lux = self._check_lux(soup)
            lux = 'No'
            if is_lux:
                # collection / luxury homes
                content_tag = soup.find('div', class_='property-details--details')
                lux = 'Yes'
            else:
                # normal apartment
                content_tag = soup.find('div', class_='property-details-body fullwidth-content-container clearfix')
            
            # append the luxury feature as an additional column
            apt_info = self._remax_apt(soup, content_tag)
            apt_info.append(lux)

        return apt_info

    def scrape_apt_urls(self, verbose=False, test=False):

        """
        A public function that allows you to call to scrape apartment URLs

        (public function)

        Parameters
        ----------
        verbose : boolean (optional)
            a flag you can enable to see the scraping progress

        test : boolean (optional)
            a flag that allows you to test run your code 
            with small sample size 

        Returns
        -------
        None
            nothing will be returned, but the attribute _apt_urls will be updated
            and all the apartments URLs will be stored in this field 
        """

        self._apt_urls = self._get_ensemble_apt_urls(verbose=verbose, test=test)

    def scrape_apt_data(self, apt_urls, verbose=False):

        """
        A public function that allows you to call to scrape apartment information

        (public function)

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
            print(f'{len(apt_urls)} apartments to be scraped')

        # loop through all the apartment URLs and scrape all the apartments
        # information in each URL
        for i, apt_url in enumerate(apt_urls):
            apt_all_data.append(self._get_apt_info(apt_url)) 
        
        self._apt_data = apt_all_data

    @property
    def apt_urls(self):
        # public attritube 
        # serve as a way to show the apt_urls
        return self._apt_urls
    
    @property
    def apt_data(self):
        # public attribute 
        # serve as a way to show the apt_data
        return self._apt_data
    
if __name__ == '__main__':

    # construct data scraping object, use Philadelphia, PA 
    # as an example
    rmdc = remax_dot_com('philadelphia', 'pa')

    # scrape all the apartment URLs in Philadelphia
    # status update enabled
    rmdc.scrape_apt_urls(verbose=True)
    urls = rmdc.apt_urls

    # in order to avoid crashes and loses all your data
    # divide the list of URLs in batches and keep updating
    # the csv file once the batch job is finished
    urls_chuck = np.array_split(urls, int(len(urls))//20)

    # try to see if the current directory has a folder 
    # that you can use to store data 
    os.chdir('..')

    # this could be modified to fit the structure of 
    # a specific user's directory
    if not os.path.exists('data'):
        os.mkdir('data')

    # sample directory inside your data directory 
    # used for test run. Of course, this could be 
    # modified based on the architecture of your 
    # own data folder 
    os.chdir('./data')
    if not os.path.exists('sample'):
        os.mkdir('sample')
    os.chdir('sample')

    # the column names of the data frame 
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

    # create an initial empty data file with all 
    # the features of an apartment
    if not os.path.exists('remax_dot_com.csv'):
        df = pd.DataFrame([], columns=cols)
        df.to_csv('./remax_dot_com.csv')

    print(f'batch jobs started, {len(urls_chuck)} batches in total')

    # running the batch and keep saving the intermediary 
    # results from the data scraping jobs 
    # each batch contains 10 URLs, but this could be modified
    for i, batch_urls in enumerate(urls_chuck):
        rmdc.scrape_apt_data(batch_urls, verbose=True)
        data = rmdc.apt_data
        df_new = pd.DataFrame(data, columns=cols)

        # append the results from each batch
        with open('remax_dot_com.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)
        print(f'batch {i} finished running')

    print('job done!')
