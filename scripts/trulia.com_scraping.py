#!/usr/bin/env python

""" 
trulia.com_scraping.py : Scrape the apartment rental infomation in trulia.com 
all the users need to do is to specify a city and state (abbreivated), as well
as the paths users want to store the actual data and the image data.

It will automatically scrape all the details related to all the apartments 
in the city users are looking at. Please note that that you need to leave a 
sufficient amount of disk space and time for this task to finish if you intend 
to run it on a local machine. 

There are three sections in this website: buy, rent and sold. Each of these 
sections has been taken care of separately. We would have separate directories
and data files for these sections. 
"""

__author__ = 'Naili Ding'
__email__ = 'nd2588@columbia.edu'
__maintainer__ = 'Naili Ding'
__version__ = '1.0.1'
__status__ = 'documentation'

### packages need to be imported 
import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np
import re
import os
import json
import datetime

### a class that contains all the contants we will be using 
class CONST:
    OVERHEAD = 'https://www.trulia.com'

    COLNAMES = {
        'buy': [
            'street', 
            'city', 
            'state', 
            'zipcode', 
            'neighborhood',
            'price',
            'bedrooms', 
            'bathrooms',
            'space',
            'extra_features',
        ],
        'rent': [
            'street', 
            'city', 
            'state', 
            'zipcode', 
            'neighborhood',
            'apartment_name',
            'bedrooms',
            'bathrooms',
            'space',
            'price',
        ],
        'sold': [
            'street', 
            'city', 
            'state', 
            'zipcode', 
            'neighborhood',
            'bedrooms', 
            'bathrooms',
            'space',
            'extra_features',
            'sales_date', 
            'sales_price', 
            'asking_price',
            'sold_date', 
            'sold_price', 
            'change_date', 
            'change_price', 
            'listing_date', 
            'listing_price',
        ],
    }

### main class
class trulia_dot_com:

    ############################
    # class initiation section #
    ############################

    def __init__(self, city, state):
        self._city = city
        self._state = state
        self._apt_urls = {
            'buy': [],
            'rent': [],
            'sold': [],
        }
        self._apt_data = {
            'buy': [],
            'rent': [],
            'sold': [],
        }

    #############################
    # private functions section #
    #############################

    def _get_buy_webpage(self, pg_num, htype):

        """
        Get the initial webpage for the buy section apartments. Each webpage
        would contain about 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        htype : list(str)
            abbreviation for house type. A list that contains the house types
            user will be considering 

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_buy_webpage(pg_num, htype)
        'https://www.trulia.com/for_sale/Philadelphia,PA/SINGLE-FAMILY_HOME,MULTI-FAMILY_type/1_p/'
        """
    
        overhead = CONST.OVERHEAD
        dangle = 'for_sale'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()
        
        dict_alias = {
            'house': 'SINGLE-FAMILY_HOME',
            'condo': 'APARTMENT,CONDO,COOP',
            'townhouse': 'TOWNHOUSE',
            'multi-family': 'MULTI-FAMILY',
            'land': 'LOT%7CLAND',
            'mobile/manufactured': 'MOBILE%7CMANUFACTURED',
            'other': 'UNKNOWN',
        }
        
        aliases = [dict_alias[h] for h in htype]
        houses = ','.join(aliases)
        
        webpage = f'{overhead}/{dangle}/{city},{state}/{houses}_type/{pg_num}_p/'

        if pg_num == 1:
            webpage = f'{overhead}/{dangle}/{city},{state}/{houses}_type/'

        return webpage

    def _get_rent_webpage(self, pg_num):

        """
        Get the initial webpage for the rent section apartments. Each webpage
        would contain roughly 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        htype : list(str)
            abbreviation for house type. A list that contains the house types
            user will be considering 

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_rent_webpage(pg_num, htype)
        'https://www.trulia.com/for_rent/Philadelphia,PA/1_p/'
        """

        overhead = CONST.OVERHEAD
        dangle = 'for_rent'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()

        webpage = f'{overhead}/{dangle}/{city},{state}/{pg_num}_p/'

        if pg_num == 1:
            webpage = f'{overhead}/{dangle}/{city},{state}/'

        return webpage

    def _get_sold_webpage(self, pg_num):

        """
        Get the initial webpage for the sold section apartments. Each webpage
        would contain roughly 30 apartments. 

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape

        htype : list(str)
            abbreviation for house type. A list that contains the house types
            user will be considering 

        Returns
        -------
        webpage : str
            the original webpage for the buy section

        >>> _get_sold_webpage(pg_num, htype)
        'https://www.trulia.com/sold/Philadelphia,PA/1_p/'
        """

        overhead = CONST.OVERHEAD
        dangle = 'sold'

        city = self._city\
                   .title()\
                   .replace(' ', '_')
        state = self._state\
                    .upper()

        # formulate the webpage
        webpage = f'{overhead}/{dangle}/{city},{state}/{pg_num}_p/'

        if pg_num == 1:
            webpage = f'{overhead}/{dangle}/{city},{state}/'

        return webpage


    def _get_soup(self, url):

        """
        This is a helper function that will automatically generate a BeautifulSoup
        object based on the given URL of the apartment webpage

        Parameters
        ----------
        url : str
            the URL of a specific apartment or a general website 

        Returns
        -------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage
        """

        # Here we added User-Agent to the header of our request 
        # It is because sometimes the web server will check the
        # different fields of the header to block robot scrapers
        # User-Agent is the most common one because it is specific 
        # to your browser.
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) \
                AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers)
        results = response.content
        if not response.status_code == 404:
            soup = BeautifulSoup(results, 'lxml')
        return soup # generate a scraper

    def _get_apt_urls_per_page(self,
                               pg_num,
                               sales_type,
                               htype=['house', 
                                      'multi-family']):

        """
        A helper function that helps the user to scrape all the apartment URLs
        in the original webpage

        Parameters
        ----------
        pg_num : int
            since there are multiple webpages, we need to specify which page
            we need to scrape
        
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        htype : list(str) (optional)
            abbreviation for house type. A list that contains the house types
            user will be considering. This will only be activated if sales_type == 'buy'
            since we don't care about the house type for rent and sold sections

        Returns
        -------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in particular
            section

        >>> _get_apt_urls_per_page()
        ['https://www.trulia.com/p/pa/philadelphia/511-s-13th-st-philadelphia-pa-19147--2090090499',
         'https://www.trulia.com/p/pa/philadelphia/1311-foulkrod-st-philadelphia-pa-19124--2017208781',
         ...
         ]
        """

        if sales_type.lower() == 'buy':
            # only buy section cares about house type
            webpage = self._get_buy_webpage(pg_num, htype)

        if sales_type.lower() == 'rent':
            webpage = self._get_rent_webpage(pg_num)

        if sales_type.lower() == 'sold':
            webpage = self._get_sold_webpage(pg_num)
        
        soup = self._get_soup(webpage)
        # main content tag
        apt_class = 'PropertyCard__PropertyCardContainer-sc-1ush98q-0 gsDQZj Box-sc-8ox7qa-0 jIGxjA'
        apt_tags = soup.find_all('div', class_=apt_class)

        # scrape all the apartment URLs
        apt_link_tags = [tag.find('a') for tag in apt_tags]
        apt_urls = [f"{CONST.OVERHEAD}{tag['href']}" for tag in apt_link_tags]
        
        return apt_urls

    def _get_apt_urls_ensemble(self,
                               sales_type,
                               htype=['house', 
                                      'multi-family'],
                               verbose=False,
                               test=False):

        """
        
        This is a helper function that will collectively scrape the apartments in 
        all of the original webpages in which each page contains roughly 30 apartments

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'
        
        htype : list(str) (optional)
            abbreviation for house type. A list that contains the house types
            user will be considering. This will only be activated if sales_type == 'buy'
            since we don't care about the house type for rent and sold sections
        
        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        urls_ensemble_cut : list(str)
            this is a list of URLs for all the apartments that we will ever care 
            in a section

        """

        stop = False # flag to tell the loop when to stop 
        urls_ensemble = [''] # a list that contains all the URLs
        pg_num = 1
        while not stop:
            # URLs per page are scraped
            urls_per_pg = self._get_apt_urls_per_page(pg_num, sales_type, htype)
            
            if verbose:
                print(f'apartment URLs in page {pg_num} all done')
            
            # if two consecutive lists of URLs are the same, we know 
            # the end of the loop has been reached
            if urls_per_pg == urls_ensemble[-1]:
                stop = True
            urls_ensemble.append(urls_per_pg)
            pg_num += 1

            if test and pg_num == 5:
                break
        
        # flatten a 2-D list
        def _flatten(lst):
            for el in lst:
                if isinstance(el, list):
                    yield from el
                else:
                    yield el
        
        # get rid of the redundant lists
        urls_ensemble_cut = list(_flatten(urls_ensemble[1:-2]))
        if verbose:
            print('last 2 pages removed since they are the same.')
        return urls_ensemble_cut

    def _load_json(self, soup):

        """
        
        A helper function that find the JSON file inside the HTML file
        This is an Easter Egg indeed 

        Parameters
        ----------
        soup : bs4.BeautifulSoup
            a scraper for a specified webpage

        Returns
        -------
        jdict : dict
            a JSON object, a dictionary of dictionaries  

        """

        jfile = soup.find('script', attrs={
            'id': '__NEXT_DATA__',
            'type': 'application/json',
        }).get_text()
        
        # convert text to JSON
        jdict = json.loads(jfile) 
        return jdict

    def _get_img_urls(self, jdict):
        """
        Find the image URLs given the JSON file of an apartment

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        urls : list(str)
            this is a list of image URLs that you directly download 

        >>> _get_img_urls(jdict)
        ['https://static.trulia-cdn.com/pictures/thumbs_6/zillowstatic/ISvgw4ch9cdv430000000000.jpg',
         'https://static.trulia-cdn.com/pictures/thumbs_6/zillowstatic/IS7mojyi16a54a1000000000.jpg',
         ...
         ]
        """

        # find photos inside the JSON file
        pics = jdict['props']['homeDetails']['media']['photos']
        urls = [pic['url']['mediumSrc'] for pic in pics]
        return urls

    def _save_images(self, 
                     img_urls, 
                     data_path, 
                     img_type, 
                     address):

        """

        Save all the images into a specific directory given the 
        downloadable image URLs

        Parameters
        ----------
        img_urls : list(str)
            this is a list of image URLs that you directly download 

        data_path : str
            the string format of the path to the directory where you
            want to save all the images

        img_type : str
            the section of the webpage, namely, 'buy', 'rent' or 'sold'

        address : str
            this is the name of the folder to contain the images of a 
            specific apartment

        Returns
        -------
        status : int
            if successful, return 1, otherwise, 0

        """

        try:
            # this is the path we want the OS to come back
            # when it finishes the image saving tasks
            current_path = os.getcwd()
            os.chdir(data_path)
            
            # create a folder for the section if it doesn't
            # exist
            if not os.path.exists(img_type):
                os.mkdir(img_type)
            os.chdir(img_type)

            # create a folder for the apartment if it doesn't
            # exist inside the section folder 
            if not os.path.exists(address):
                os.mkdir(address)
            os.chdir(address)

            # write images inside the apartment folder 
            for i, img_url in enumerate(img_urls):
                img_data = requests.get(img_url).content
                with open(f'img{i}.jpg', 'wb') as handler:
                    handler.write(img_data)
            
            # go back to the original path before the 
            # function was initiated 
            os.chdir(current_path)
            return 1
        
        except:
            return 0

    def _get_address(self, jdict):
        
        """

        A helper function that gets the address info of the apartment given 
        the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        tuple
            address information

        >>> _get_address(jdict)
        ('302 Carpenter Ln', 'Philadelphia', 'PA', '19119', 'Mount Airy West')

        """
        
        try:
            # access the location info dictionary
            loc_dict = jdict['props']['homeDetails']['location']
            state = loc_dict['stateCode']
            city = loc_dict['city']
            zipcode = loc_dict['zipCode']
            street = loc_dict['formattedLocation']
            try:
                neighborhood = loc_dict['neighborhoodName']
            except:
                neighborhood = None
            return street, city, state, zipcode, neighborhood
        except:
            return None, None, None, None, None

    def _get_price(self, jdict):

        """

        A helper function that gets the price info of the apartment given 
        the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        float
            price of the apartment

        >>> _get_price(jdict)
        650000.0

        """

        try:
            price_dict = jdict['props']['homeDetails']['price']
            return float(price_dict['price'])
        except:
            return None

    def _get_bedrooms_bathrooms(self, jdict):

        """

        A helper function that gets the bedroom and bathroom info of the 
        apartment given the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        tuple
            # of bedrooms and # of bathrooms

        >>> _get_bedrooms_bathrooms(jdict)
        (5.0, 3.0)

        """

        try:
            pattern = r'[-+]?\d*\.\d+|\d+'
            bed_dict = jdict['props']['homeDetails']['bedrooms']
            bath_dict = jdict['props']['homeDetails']['bathrooms']
            bedrooms = re.findall(pattern, bed_dict['summaryBedrooms'])[0]
            bathrooms = re.findall(pattern, bath_dict['summaryBathrooms'])[0]
            return float(bedrooms), float(bathrooms)
        except:
            return np.nan, np.nan

    def _get_space(self, jdict): 

        """

        A helper function that gets the square foot of the apartment given 
        the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        float
            the area of the apartment in square foot 

        >>> _get_space(jdict)
        3012.0

        """

        try:
            space_dict = jdict['props']['homeDetails']['floorSpace']
            space_text = space_dict['formattedDimension'].replace(',','')
            space = self._extract_num(space_text)
            return space
        except:
            return np.nan

    def _get_apt_features(self, jdict):

        """

        A helper function that gets the extra features of the apartment 
        given the JSON file

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries that contains all 
            the data you would find in a webpage of the targeted apartment

        Returns
        -------
        str
            we stick all the extra features in a string separted by '|'
            since each apartment has its unique bonus features, it would 
            be infeasible to make them into columns

        >>> _get_apt_features(jdict)
        'Townhouse | $29/sqft | Lot Size:1,035 sqft | Built in 1940 | 6 Rooms | \
        Rooms:Dining Room | Heating:Forced Air | Heating Fuel:Gas | Cooling System:Central | \
        Air Conditioning | Great Views | Colonial Architecture | Stories:2 | Exterior:Brick | \
        Disabled Access'
        
        """

        try:
            fdict_list = jdict['props']['homeDetails']['features']['attributes']
            features = []
            for fdict in fdict_list:
                # find the extra features 
                try:
                    value = fdict['formattedValue']
                    try:
                        key = fdict['formattedName']
                        features.append(f'{key}:{value}')
                    except:
                        features.append(value)
                except:
                    next
            # stick all the features together, seperated by |
            return ' | '.join(features)
        except:
            return None

    def _get_buy_apt_data(self, 
                          apt_urls, 
                          verbose=False, 
                          test=False):

        """

        A function that collects all the data we will need for an apartment in 
        the buy category

        Parameters
        ----------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        apt_info_data : list
            all the relevant apartment information data        

        """

        apt_info_data = []

        for url in apt_urls:
            soup = self._get_soup(url)
            jdict = self._load_json(soup)
            street, city, state, zipcode, neighborhood = self._get_address(jdict)
            price = self._get_price(jdict)
            bedrooms, bathrooms = self._get_bedrooms_bathrooms(jdict)
            space = self._get_space(jdict)
            features = self._get_apt_features(jdict)

            apt_info_data.append([
                street, 
                city, 
                state, 
                zipcode, 
                neighborhood,
                price,
                bedrooms, 
                bathrooms,
                space,
                features,
            ])

        return apt_info_data

    def _get_section_data(self, section):
        
        """

        A helper function to scrape rent apartment data based on the 
        section dictionary 

        Parameters
        ----------
        section : dict
            A dictionary that contains the floor plan information

        Returns
        -------
        section_data : list
            the apartment unit data

        >>> _get_section_data(section)
        ['2 Bed/2 Bath-B9', 2.0, 2.0, 1155.0, nan]
        """
        
        # unit number
        apt_name = section['name']
                
        try:
            # get the number of bedrooms and bathrooms based 
            # on the specific section dictionary
            bedrooms_text = section['bedrooms']['fullValue']
            bathrooms_text = section['bathrooms']['fullValue']
            bedrooms = self._extract_num(bedrooms_text)
            bathrooms = self._extract_num(bathrooms_text)
        except:
            bedrooms, bathrooms = np.nan, np.nan

        try:
            # get the square foot area of the unit 
            space = float(section['floorSpace']['max'])
        except:
            space = np.nan

        try:
            # get the rent price of the unit 
            price_text = section['priceRange']['formattedPrice']
            price_text = price_text.replace(',', '') \
                                   .replace('$', '')
            price = self._extract_num(price_text)
        except:
            price = np.nan
            
        # construct the section data
        section_data = [
            apt_name,
            bedrooms,
            bathrooms,
            space,
            price,
        ]
        
        return section_data

    def _extract_num(self, text):
        """
        A helper function that extract any number from
        a text 

        Parameters
        ----------
        text : str
            a string of text that might contains numbers 

        Returns
        -------
        num : float
            the number extracted from the text 

        >>> _extract_num('$1000 per month')
        1000.0
        """
        try:
            if 'studio' in text.lower():
                return 0.0
            pattern = r'[-+]?\d*\.\d+|\d+'
            result = re.findall(pattern, text)[0]
            return float(result)
        except:
            return np.nan

    def _get_floorplans(self, jdict):
        
        """
        This is a helper function that extract the floorplan information of 
        the rental apartments. The structure is very similar to rent.com

        Parameters
        ----------
        jdict : dict
            a JSON object, a dictionary of dictionaries 

        Returns
        -------
        rental_data : list
            rental data, similar to rent.com
        """
        
        try:
            floorplans_groups = jdict['props']['homeDetails']['floorPlans']['floorPlanGroups']
            address_data = list(self._get_address(jdict))
            rental_data = []
            
            # different floorplans, e.g. studio, 1 bedroom 1 bathroom etc.
            for floorplans in floorplans_groups:
                plans = floorplans['plans']
                for section in plans:
                    # this is the header 
                    section_data = self._get_section_data(section)
                    rental_data.append(address_data+section_data)
                    units = section['units']
                    # these are all the units under that header 
                    for unit in units:
                        unit_data = self._get_section_data(unit)
                        rental_data.append(address_data+unit_data)
            return rental_data
        except:
            return None

    def _get_rent_apt_data(self, 
                           apt_urls, 
                           verbose=False, 
                           test=False):

        """
        This is a helper function that packages all the helper function regarding
        rental information extraction together 
        """

        apt_info_data = []

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            try:
                soup = self._get_soup(apt_url)
                jdict = self._load_json(soup)
                floorplan_data = self._get_floorplans(jdict)
                if floorplan_data:
                    apt_info_data += floorplan_data

                if test and i==5:
                    break
            except:
                continue

        return apt_info_data

    def _first(self, 
               iterable, 
               condition=lambda x: True):
        """
        Returns the first item in the 'iterable' that
        satisfies the 'condition'.

        If the condition is not given, returns the first item of
        the iterable.

        Return None if no item satysfing the condition is found.

        >>> first((1,2,3), condition=lambda x: x%2 == 0)
        2
        >>> first(range(3, 100))
        3
        """
        try:
            return next(x for x in iterable if condition(x))
        except:
            return None

    def _get_historical_prices_dict(self, jdict):
        """
        find the historical price dictionary 
        """
        try:
            price_history = jdict['props']['homeDetails']['priceHistory']
            price_sold = self._first(price_history, 
                               condition=lambda x: x['event'].lower() == 'sold')
            price_listed = self._first(price_history,
                                condition=lambda x: x['event'].lower() == 'listed for sale')
            try:
                start, end = price_history.index(price_sold), price_history.index(price_listed)
                price_history = price_history[start:end]
                price_change = self._first(price_history,
                                    condition=lambda x: x['event'].lower() == 'price change')
                return price_sold, price_change, price_listed
            except:
                return price_sold, None, price_listed
        except:
            return None, None, None

    def _unzip_pdict(self, price_dict):
        """
        helper function to unzip the price dictionary in the json file 
        """
        try:
            price_text = price_dict['price']['formattedPrice'].replace('$', '')\
                                                              .replace(',', '')
            price = self._extract_num(price_text)
            date = price_dict['formattedDate']
            date_formatted = datetime.datetime\
                                     .strptime(date, '%m/%d/%Y')\
                                     .strftime('%Y-%m-%d')
            return date_formatted, price
        except:
            return None, None

    def _get_normal_sold_prices(self, jdict):
        """
        get the normal price information, for example, sales price and asking price
        """
        price_dict = jdict['props']['homeDetails']['price']
        try:
            sales_price_text = price_dict['formattedPrice'].replace(',','')\
                                                           .replace('$', '')
            sales_price = self._extract_num(sales_price_text)
            sales_date = price_dict['formattedSoldDate']
            sales_date_formatted = datetime.datetime\
                                           .strptime(sales_date, '%b %d, %Y')\
                                           .strftime('%Y-%m-%d')
            try:
                asking_price_text = price_dict['listingPrice']['formattedPrice'].replace(',','')\
                                                                                .replace('$', '')
                if 'k' in asking_price_text.lower():
                    asking_price = self._extract_num(asking_price_text)*1e3
                elif 'm' in asking_price_text.lower():
                    asking_price = self._extract_num(asking_price_text)*1e6
                else:
                    asking_price = self._extract_num(asking_price_text)
                return sales_date_formatted, sales_price, asking_price
            except:
                return sales_date_formatted, sales_price, np.nan
        except:
            return None, None, None
    

    def _get_important_sold_prices(self, jdict):
        """
        Get all the historical price information
        latest price sold, price change, and price listed 
        along with the corresponding dates 
        """
        pdict_s, pdict_c, pdict_l = self._get_historical_prices_dict(jdict)
        date_s, price_s = self._unzip_pdict(pdict_s)
        date_c, price_c = self._unzip_pdict(pdict_c)
        date_l, price_l = self._unzip_pdict(pdict_l)
        
        return date_s, price_s, date_c, price_c, date_l, price_l

    def _get_sold_info(self, jdict):
        """
        A helper function that packages all the sold apartment information
        """
        street, city, state, zipcode, neighborhood = self._get_address(jdict)
        bedrooms, bathrooms = self._get_bedrooms_bathrooms(jdict)
        space = self._get_space(jdict)
        features = self._get_apt_features(jdict)
        sales_date, sales_price, ask_price = self._get_normal_sold_prices(jdict)
        sold_date, sold_price, change_date, change_price, list_date, list_price = self._get_important_sold_prices(jdict)
        
        sold_info = [
            street, 
            city, 
            state, 
            zipcode, 
            neighborhood,
            bedrooms, 
            bathrooms,
            space,
            features,
            sales_date, 
            sales_price, 
            ask_price,
            sold_date, 
            sold_price, 
            change_date, 
            change_price, 
            list_date, 
            list_price,
        ]
        
        return sold_info

    def _get_sold_apt_data(self, 
                           apt_urls, 
                           verbose=False, 
                           test=False):

        """
        
        This is a helper function that helps you obtain all the 
        sold apartments information. Please note that the information
        we need about the apartments differ when we have different types 
        of apartments. 

        Parameters
        ----------
        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        apt_info_data : list
            a list that contains all the information regarding the sold apartments 

        >>> _get_sold_apt_data(apt_urls)
        [['4419 Wayne Ave',
         'Philadelphia',
         'PA',
         '19140',
         'Logan',
         3.0,
         1.0,
         1188.0,
         'Townhouse | $29/sqft | Lot Size:1,035 sqft | Built in 1940 | 6 Rooms \
                | Rooms:Dining Room | Heating:Forced Air | Heating Fuel:Gas | \
                Cooling System:Central | Air Conditioning | Great Views | \
                Colonial Architecture | Stories:2 | Exterior:Brick | Disabled Access',
         '2019-11-15',
         35000.0,
         36000.0,
         '2019-11-15',
         35000.0,
         '2019-10-26',
         36000.0,
         '2019-10-10',
         45000.0], .... ]

        """

        apt_info_data = []

        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, apt_url in enumerate(apt_urls):
            soup = self._get_soup(apt_url)
            jdict = self._load_json(soup)
            sold_data = self._get_sold_info(jdict)
            apt_info_data.append(sold_data)

            if test and i==5:
                break

        return apt_info_data

    ############################
    # public functions section #
    ############################

    def scrape_apt_urls(self, 
                        sales_type,
                        htype=['house', 
                               'multi-family'],
                        verbose=False, 
                        test=False):

        """
        
        The main function you can use to scarpe the apartment URLs, the users only
        need to specify what sales_type the apartment is 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        htype : list(str) (optional)
            abbreviation for house type. A list that contains the house types
            user will be considering. This will only be activated if sales_type == 'buy'
            since we don't care about the house type for rent and sold sections

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the data will be saved in the private field of this class

        """
        
        sales_type = sales_type.lower()
        self._apt_urls[sales_type] = self._get_apt_urls_ensemble(sales_type, 
                                                                 htype, 
                                                                 verbose, 
                                                                 test)

    def scrape_apt_data(self, 
                        sales_type,
                        apt_urls,
                        verbose=False, 
                        test=False):

        """
        
        The main function you can use to scarpe the apartment data, the users only
        need to specify what sales_type the apartment is, as well as the apartment URLs

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the data will be saved in the private field of this class

        """

        # check which type of sales the user want to scrape 
        if sales_type == 'buy':
            self._apt_data['buy'] = self._get_buy_apt_data(apt_urls, verbose, test)
        if sales_type == 'rent':
            self._apt_data['rent'] = self._get_rent_apt_data(apt_urls, verbose, test)
        if sales_type == 'sold':
            self._apt_data['sold'] = self._get_sold_apt_data(apt_urls, verbose, test)


    def scrape_apt_images(self, 
                          sales_type,
                          apt_urls,
                          data_path,
                          verbose=False, 
                          test=False):

        """
        
        Based on the sales type, the scraper will automatically write the images onto 
        the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_urls : list(str)
            this is a list of URLs of the apartments in the original webpage in 
            particular section

        data_path : str
            the string of the path to where you want to store the images 

        verbose : boolean (optional)
            text update on the process to help grasp what's going on with the scraping 

        test : boolean (optional)
            a handler for debugging purposes, only allowing a small chunk of data to 
            be processed to avoid runtime issues

        Returns
        -------
        None
            the images will be saved onto the local machine 

        """


        if verbose:
            print(f'a total number of {len(apt_urls)} apartments to be scraped')

        for i, url in enumerate(apt_urls):

            if test and i == 5:
                break

            soup = self._get_soup(url) # get a soup object
            jdict = self._load_json(soup) # extract the json file 
            img_urls = self._get_img_urls(jdict) # extract image URLs from the json file
            address = self._get_address(jdict)[0].upper() # name of the folder 
            # write images onto the local machine 
            self._save_images(img_urls, 
                              data_path, 
                              sales_type,
                              address)

        if verbose:
            print(f'images in a total number of {len(apt_urls)} apartments have been scraped')

    def write_data(self,
                   sales_type,
                   apt_data, 
                   data_path):

        """
        
        Based on the sales type, the scraper will automatically write the apartment data 
        onto the local machine. Please note that if 'test' is opted out, the size of the 
        images will become significant. 

        Parameters
        ----------
        sales_type : str
            a handler to tell the function which section you're looking at, e.g. 'buy'

        apt_data : list(object)
            this is a list of apartment data in raw format and later on will be used 
            to construct the dataframe 

        data_path : str
            the string of the path to where you want to store the images 

        Returns
        -------
        None
            the data will be saved onto the local machine 

        """

        # this is the path the OS will go back eventually
        current_path = os.getcwd() 
        os.chdir(data_path) # get into the data directory

        # check if the data exists, if not, create a new data file
        if not os.path.exists(f'trulia_dot_com_{sales_type}.csv'):
            df = pd.DataFrame([], columns=CONST.COLNAMES[sales_type])
            df.to_csv(f'trulia_dot_com_{sales_type}.csv')

        # continuously write into the existing data file on the local machine 
        df_new = pd.DataFrame(apt_data, columns=CONST.COLNAMES[sales_type])
        with open(f'trulia_dot_com_{sales_type}.csv', 'a') as df_old:
            df_new.to_csv(df_old, header=False)

        # go back to the path where it is originally located 
        os.chdir(current_path)


    #####################
    # public attributes #
    #####################

    @property
    def apt_urls(self):
        """
        A public attribute that lets you get access to all
        of the apartment URLs that need to be scraped. Notice
        that this is essentially a dictionary
        """
        return self._apt_urls

    @property
    def apt_data(self):
        """
        A public attribute that lets you get access to all
        of the apartment data that need to be scraped.
        """
        return self._apt_data


if __name__ == '__main__':

    # users need to specifiy the path where you want to
    # store the data by changing img_path and data_path
    img_path = '../data/sample/trulia/imgdata'
    data_path = '../data/sample/trulia/aptdata'
    
    # different sales categories 
    categories = ['sold', 'buy', 'rent']
    # construct a scraper object
    tdc = trulia_dot_com('philadelphia', 'pa')

    # scrape different streams of apartments iteratively 
    # could be optimized by parallel programming 
    for category in categories:
        print(f'scraping for category - {category} starts!')
        tdc.scrape_apt_urls(category, verbose=True)

        # divide the apartment URLs list into small batches 
        # in case the program crashes 
        apt_urls = tdc.apt_urls[category]
        url_batches = np.array_split(apt_urls, int(len(apt_urls))//20)

        # batch jobs start
        print(f'a total number of {len(url_batches)} batches')
        for i, url_batch in enumerate(url_batches):
            try:
                print(f'batch {i} starts')
                print(url_batch)
                tdc.scrape_apt_data(category, url_batch, verbose=True)
                data = tdc.apt_data[category]

                tdc.write_data(category, data, data_path)
                tdc.scrape_apt_images(category, url_batch, img_path, verbose=True)
            except:
                print(f'batch {i} failed')
                print(f'unscraped URLs: {url_batch}')
                continue

        print(f'scraping for category - {category} done!')

    print('job done, congratulations!')
