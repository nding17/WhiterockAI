# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 15:27:29 2019

@author: Quinntang
"""

## import necessary packages
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import urllib as ulb
import random
import time
import re
import os

class coldwell_dot_com:

    def __init__(self, city, state, start_page, end_page):
        self._city = city
        self._state = state
        self._start_page = start_page
        self._end_page = end_page

    def _get_link_content(self, url):
        ##Decorate the request with header and proxy
        my_headers=[
            "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",
            "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
        ]

        headers = [
            ('Host', 'https://www.coldwellbankerhomes.com'), 
            ('Connection', 'keep-alive'), 
            ('Cache-Control', 'max-age=0'),
            ('User-Agent', random.choice(my_headers)),
        ]

        ##Please note the the size of proxy IPs may affect the performance,if the IP pools are small, may raise 403 Error (Server Forbidden)
        proxy_list = '138.197.222.35,36.89.65.253,105.19.59.192,109.110.73.106,176.9.75.42,200.89.178.63,138.68.161.14,188.226.141.61,139.59.109.156'.split(',')
        ##Add timer to sleep for 1 sec,in order to avoid getting blocked
        t = 1
        time.sleep(t)
        ##Decorate the url request with Header and Proxy IP
        proxy = random.choice(proxy_list)

        urlhandle = ulb.request.ProxyHandler({'http': proxy})
        opener = ulb.request.build_opener(urlhandle)
        opener.addheaders = headers
        ulb.request.install_opener(opener)
        response = ulb.request.Request(url)
        
        fp = ulb.request.urlopen(response)
        html = fp.read()
        fp.close
        content = BeautifulSoup(html,"lxml")
        return content
    
    def _get_content(self, url, img_path):
        
        listing_content = self._get_link_content(url)
        
        ## Scrap the address, city, state, zip_code, apt #, asking price
        address = listing_content.find('h1', class_='notranslate') \
                                 .find('span', class_='notranslate') \
                                 .get_text() \
                                 .strip() \
                                 .split(',')

        city = address[1].strip()
        state = address[2].strip().split(' ')[0].strip()
        zip_code = address[2].strip().split(' ')[1].strip()
        if len(address[0].split('#'))>1:
            street = address[0].split('#')[0].strip()
            apt_num = address[0].split('#')[1].strip()
        else:
            street = address[0].split('#')[0].strip()
            apt_num = 'N/A'
        asking_price = listing_content.find('span', itemprop='price').get_text()
        
        # Scrap the number of bedrooms,full bathroom, sqt, listing type
        title = str()
        for item in listing_content.find_all('ul', class_='details'):
            title += item.get_text().strip()
        try:
            listing_type = title.split('\n')[2]
            bedrooms = re.findall(r'[0-9]+ Bed\w?', title)[0].split(' ')[0]
            bathrooms = re.findall(r'[0-9]+ Full Bath\w?', title)[0].split(' ')[0]
            sqt = re.findall(r'[0-9]+ Sq. Ft', title)[0].split(' ')[0]
        except:
            bedrooms, bathrooms = 'N/A', 'N/A'
            try:
                sqt = re.findall(r'[0-9]+ Sq. Ft', title)[0].split(' ')[0]
            except:
                sqt = np.nan
            listing_type = title.split('\n')[2]

        ## Scrap all the other informations for this property
        details = str()
        for item in listing_content.find_all('li'):
            details+= item.get_text()+'\n'       
        for item in details.split('\n'):
            if re.findall(r'Construction:', item)!=[]:
                material = item.split(':')[1].strip()
                break
            else:
                material = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Lot Size', item):
                if item.split(':')[0] == 'Lot Size (Acres)':
                    lot_size = item.split(':')[1].strip()
                    break
            else:
                lot_size = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Basement:', item):
                base = item.split(':')[1].strip()
                break
            else:
                base = 'N/A'
        for item in details.split('\n'):      
            if re.findall(r'Basement Desc.:', item):
                base_desc = item.split(':')[1].strip()
                break
            else:
                base_desc = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Year Built:', item):
                year_built = item.split(':')[1].strip()
                break
            else:
                year_built = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Stories/Levels',item):
                floors = item.split(':')[1].strip()
                break
            else:
                floors = 'N/A'
        for item in details.split('\n'):
            if re.findall(r'Architectural Info',item):
                arch_info = item.split(':')[1].strip()
                break
            else:
                arch_info = 'N/A'
                
        listing_detail = {
            'ADDRESS': street,
            'CITY': city, 
            'STATE': state, 
            'ZIP': zip_code, 
            'APT': apt_num, 
            'BATHROOMS': bathrooms,
            'BEDROOMS': bedrooms, 
            'SF': sqt,
            'ASKING PRICE': asking_price, 
            'LISTING TYPE': listing_type,
            'LOT SF': lot_size, 
            'YEAR BUILT': year_built, 
            'FLOORS': floors, 
            'BASEMENT': base,
            'BASEMENT DESC': base_desc, 
            'ARCH': arch_info, 
            'MATERIAL': material
        }

        ##Scrap all the image for each property and store them into each folder
        ##Please change the file_root accordingly when tested
        image_url = []
        for image_link in listing_content.find_all('img',class_="owl-lazy"):
            image_url.append(image_link.get('data-href'))

        file_root = img_path
        file_folder = ','.join([street,city])
        file_path = os.path.join(file_root, file_folder)

        current_path = os.getcwd() 
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        os.chdir(file_path)

        for i in range(len(image_url)):
            f= open("{} {}.jpg".format(street,i+1),"wb")
            f.write(ulb.request.urlopen(image_url[i]).read())
            f.close

        os.chdir(current_path)
            
        return listing_detail

    def _get_df(self, content_list, save_to_excel=False):
        ## Store all the listing info to a dataframe, if choose to save as Excel Spread Sheet, pass True
        df = pd.DataFrame()
        for i in range(len(content_list)):
            temp_df = pd.DataFrame(content_list[i],index=[i])
            df = pd.concat([df,temp_df],axis=0, ignore_index=True)
        if not save_to_excel:
            df.to_excel("Phil_demo_data_2.xlsx")
        return df

    def _get_max_page(self):
        url = 'https://www.coldwellbankerhomes.com/pa/philadelphia/?sortId=2&offset=0'
        content = self._get_link_content(url)
        pg_list = content.find('ul', class_='propertysearch-results-pager')
        pages = pg_list.find_all('li')
        max_pg = pages[-2].get_text()
        return int(max_pg)

    def scraping_pipeline(self, data_path, img_path):
        print(f'Coldwell Bankers For Sale - Start Scraping!')
        if self._end_page == 'max':
            self._end_page = self._get_max_page()

        ##Test the function and integrate the results
        url_list = ['https://www.coldwellbankerhomes.com/{}/{}?sortId=2&offset={}' \
                    .format(self._state, self._city, (i-1)*24) \
                    for i in range(self._start_page, self._end_page+1)]

        listing_link = []

        for url in url_list:
            content = self._get_link_content(url)
            for listing in content.find_all('div', class_="address notranslate"):
                listing_link.append('https://www.coldwellbankerhomes.com'+listing.find('a')['href'])

        content_list = []
        print(f'\ttotal number of pages to be scraped: {len(content_list)}')
        for i, url in enumerate(listing_link):
            content_list.append(self._get_content(url, img_path))
            print(f'\tscraping for page # {i+1} is done')
        
        df = self._get_df(content_list, save_to_excel=True)
        df.to_csv(f'{data_path}/coldwell_dot_com.csv')
        print('job done!')

if __name__ == '__main__':
    data_path = '../data/sample'
    img_path = '../data/sample/coldwell'
    cdc = coldwell_dot_com('philadelphia', 'pa', 1, 'max')
    cdc.scraping_pipeline(data_path, img_path)