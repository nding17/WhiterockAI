# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 08:58:57 2019

@author: jorda
"""
import requests
import lycleaner
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np
import urllib
import os
import csv
import urllib.request
import html.parser
from requests.exceptions import HTTPError
from socket import error as SocketError
from http.cookiejar import CookieJar
import datetime
import time
import random
from fake_useragent import UserAgent
import sys
import warnings
if not sys.warnoptions:
    warnings.simplefilter('ignore')
    
cleaner = lycleaner.Address_cleaner()
ua = UserAgent()
ua.update()
try:
    ua = UserAgent()
    
except FakeUserAgentError:
    print(ua.random)
    
################################# Loopnet Residential on sale ##############################
def get_loopnet_id():    
    """
    Get Residential URL
    
    Returns
    -------
    keep : list
        a list of Residential URL
    """    
    for i in range(1,21):
        url = r'https://www.loopnet.com/new-york_multifamily-properties-for-sale/'+str(i)+'/'
        headers ={'User-Agent': ua.random}
        res = requests.get(url, headers=headers)
        page_content = BeautifulSoup(res.content,'lxml')
        if i == 1:
            print(i)
            ID = [l['href'] for l in page_content.findAll('a',href=re.compile(r'/Listing/.+/\d{8}/'))]

        else:
            print(i)
            temp = [l['href'] for l in page_content.findAll('a',href=re.compile(r'/Listing/.+/\d{8}/'))]

            ID.extend(temp)
        time.sleep(15)
    return ID

def get_info(id_):
    """
    Get building information with the ID
    ----------
    id_ : str
        Building Listing ID
    Returns
    -------
    final_table1, final_table2 : DataFrame
        two tables for a building
    """    
    url = 'https://www.loopnet.com'+id_
    headers ={'User-Agent': ua.random}
    req = requests.get(url=url,headers=headers)
    page_content = BeautifulSoup(req.text, 'lxml')
    
    def get_address():
        tag = page_content.find_all('h2')[-1]
        tag1 = page_content.findAll('h1', class_='profile-hero-title')
        address = tag.get_text().replace('ABOUT','').replace('\r','').replace('\n','').split(',')
        title = [t.text for t in tag1]
        df = pd.DataFrame([['Address',' - '.join(address)], ['Title',title[0]]])

        return df
    
    def get_tables():   
        tables = page_content.select('table')
        df_list = []
        
        for table in tables:
            df_list.append(pd.concat(pd.read_html(table.prettify())))
        
        if 'Financial Summary' in str(df_list[2].columns[0]):
            table1, table2 = df_list[0], df_list[2]
            
        else:
            table1, table2 = df_list[0], pd.DataFrame()
        
        table_new  = table1.iloc[:,:2].append(pd.DataFrame(table1.iloc[:,2:].values))
        
        if not table2.empty:
            table2_new = table2.iloc[:,:-1]
            table2_new.columns = [0,1]
            table_new = pd.concat([table_new, table2_new],ignore_index = True)
            
        return table_new.dropna()
    
    def get_timestamp():
        t = page_content.findAll('ul', class_='property-timestamp')
        results = [tt.text for tt in t][0]
        time = results.strip('\n').split('\n')
        time = pd.Series(time)
        time = pd.DataFrame(time.str.split(': ', n=1, expand=True))
        return time

    def get_link():
        link = pd.DataFrame(['Link',url]).T
        return link
    
    def get_salesnote():
        try:
            notes = page_content.find('section', class_='description include-in-page').get_text()
            return pd.DataFrame([notes.replace('\n','').strip().split('\r')[0], notes.replace('\n','').strip().split('\r')[-1]]).T
        except AttributeError:
            print('There is not Sales Notes')
            return pd.DataFrame()
    
    Address = get_address()
    Table = get_tables()
    Time = get_timestamp()
    Link = get_link()
    Sale_note = get_salesnote()

    final_table1 = pd.concat([Address, Table, Time, Link, Sale_note],ignore_index = True).set_index([0]).T
    if 'Total Expenses' in final_table1.columns:
        final_table1 = final_table1.drop(['Other Income', 'Total Expenses'],1)
    
    return final_table1

def get_tables(ID):   
    """
    Get all building information with the ID
    ----------
    ID : list
        a list of Building Listing ID
    Returns
    -------
    final_table1, final_table2 : DataFrame
        two tables for all buildings
    """    
    global loopnet_residential_scrape_error
    loopnet_residential_scrape_error = []         
    for i in range(len(ID)):
        try:
            if i == 0:
                print(i, ID[i])
                table1 = get_info(ID[i])
                if 'Total Building Size' in table1.columns:
                    table1.rename(columns={'Total Building Size':'Building Size'},inplace = True)
                    table1.rename(columns={'Total Land Area':'Lot Size'},inplace = True)
        
        
            else:
                print(i, ID[i])
                temp1 = get_info(ID[i])
                if 'Total Building Size' in temp1.columns:
                    temp1.rename(columns={'Total Building Size':'Building Size'},inplace = True)
                    temp1.rename(columns={'Total Land Area':'Lot Size'},inplace = True)
        
        
                table1 = pd.concat([table1,temp1],ignore_index = True)
                time.sleep(10)
        except:
            loopnet_residential_scrape_error.append(ID[i])
            pass    
    return table1

def loopnet_residential_cleaner(loopnet_residential_df):
    """
    Clean all building information
    ----------
    loopnet_residential_df : pd.DataFrame
        a dataframe of building information
    Returns
    -------
    loopnet_residential_df : pd.DataFrame
        a cleaned building information dataframe
    """    
    loopnet_residential_df['Address'] = loopnet_residential_df['Address'].apply(lambda x: x.strip())
    loopnet_residential_df[['Address','Zip']]= loopnet_residential_df['Address'].str.split(r" NY ",expand = True)
    loopnet_residential_df['Cap Rate'].fillna(loopnet_residential_df['Address'].apply(lambda x: re.findall(r'[-\d.]+\d%',x)[0] if re.findall(r'[-\d.]+\d%',x) != [] else np.nan),inplace = True)
    loopnet_residential_df['Price'].fillna(loopnet_residential_df['Address'].apply(lambda x: re.findall(r"\$\d+ - \d+ - \d+|\$\d+ - \d+", x)[0].replace(' - ',',') if re.findall(r"\$\d+ - \d+ - \d+|\$\d+ - \d+", x) != [] else np.nan),inplace=True)
    loopnet_residential_df['Address'] = loopnet_residential_df['Address'].str.split(r" - .+",expand = True)[0]
    loopnet_residential_df['Title'] = loopnet_residential_df['Title'].str.split(r" - .+",expand = True)[0]
    loopnet_residential_df['Address'] = loopnet_residential_df['Address'].apply(lambda x: np.nan if 'Unit' in str(x) or '$' in str(x) or 'Properties' else x)
    loopnet_residential_df['Address'] = loopnet_residential_df['Address'].fillna(loopnet_residential_df['Title'])
    loopnet_residential_df['Address'] = loopnet_residential_df['Address'].replace(regex={' Portfolio':''})
    loopnet_residential_df = loopnet_residential_df[loopnet_residential_df['Address'].apply(lambda x: x[0].isnumeric())]
    loopnet_residential_df['State'] = 'NY'
    loopnet_residential_df = loopnet_residential_df[loopnet_residential_df['Link'].apply(lambda x: 'portfolio' not in x)]
    loopnet_residential_df.dropna(subset = ['Address'], inplace = True)
    loopnet_residential_df['Address'] = cleaner.easy_clean(loopnet_residential_df['Address'].str.upper().astype('str'))
    loopnet_residential_df.columns = [c.capitalize() for c in loopnet_residential_df.columns]
    loopnet_residential_df = loopnet_residential_df[['Address', 'Apartment style', 'Average occupancy','Building class', 'Building size', 'Cap rate',
           'Date created', 'Effective gross income', 'Floors','Gross rent multiplier', 'Gross rental income','Last updated', 'Link', 'Listing id', 'Lot size',
           'Net operating income', 'No. stories', 'No. units', 'Operating expenses','Price','Price / sf', 'Property sub-type', 
           'Property type','Taxes', 'Unit size','Vacancy loss', 'Year built', 'Zip','Investment summary', 'Sale notes', 'State']]
    
    loopnet_residential_df[['Building size']] = loopnet_residential_df[['Building size']].replace(regex = {' SF':'',',':''})
    loopnet_residential_df[['Operating expenses','Effective gross income','Gross rental income','Net operating income','Price','Price / sf','Taxes','Vacancy loss']]=loopnet_residential_df[['Operating expenses','Effective gross income','Gross rental income','Net operating income','Price','Price / sf','Taxes','Vacancy loss']].replace(regex = {'\$': '', ',': ''})
    loopnet_residential_df[['Operating expenses','Vacancy loss','Taxes','Price']] = loopnet_residential_df[['Operating expenses','Vacancy loss','Taxes','Price']].replace(regex = {'Upon Request':'','-':np.nan})
    loopnet_residential_df.rename(columns = {'Property sub-type':'Sub-type','Listing id':'Listing ID'},inplace = True)
    return loopnet_residential_df

################################# Loopnet Residential off market ##############################
def get_loopnet_history_id():    
    """
    Get Residential URL
    
    Returns
    -------
    keep : list
        a list of Residential URL
    """    
    for i in range(1,1000):
        url = r'https://www.loopnet.com/New-York_Investment-Properties-Sold/{}/'.format(i)
        headers ={'User-Agent': ua.random}
        res = requests.get(url, headers=headers)
        page_content = BeautifulSoup(res.content,'lxml')
        if i == 1 and page_content.head.title.text != '404 Page Not Found':
            print(i)
            link = [l['href'] for l in page_content.findAll('a',href=re.compile(r'/Listing/\d{8}/.+/'))]

        elif page_content.head.title.text != '404 Page Not Found':
            print(i)
            temp = [l['href'] for l in page_content.findAll('a',href=re.compile(r'/Listing/\d{8}/.+/'))]

            link.extend(temp)
            time.sleep(15)
        else:
            break
    return link

def get_loopnet_history_info(id_):
    """
    Get building information with the ID
    ----------
    id_ : str
        Building Listing ID
    Returns
    -------
    final_table1, final_table2 : DataFrame
        two tables for a building
    """    
    url = 'https://www.loopnet.com'+id_
    #url = 'https://www.loopnet.com/Listing/20401913/1083-Fifth-Ave-New-York-NY/'
    ip_list = ['119.6.136.122','114.106.77.14']
    proxies = {"http": random.choice(ip_list)}    
    headers ={'User-Agent': ua.random}
    req = requests.get(url=url,headers=headers,proxies=proxies)
    page_content = BeautifulSoup(req.text, 'lxml')
    
    def get_address():
        #tag = page_content.find_all('h2')[-1]
        address = page_content.find('div', class_ = 'column-12 property-info')
        address = address.text.split('\r')
        address = [a.strip('\n').strip() for a in address]
        address = [a for a in address if len(a)>2]
        df = pd.DataFrame([['Address',address[0].strip()], ['Zip',address[1]], ['Type',address[2].strip()]])
        return df
    
    def get_tables():   
        tables = page_content.select('table')
        df_list = []
        
        for table in tables:
            df_list.append(pd.concat(pd.read_html(table.prettify())))
        
        info = df_list[0].iloc[:,0:2].append(pd.DataFrame(df_list[0].iloc[:,2:].values), ignore_index=True)
        time = df_list[1].T
        time = pd.DataFrame(time.iloc[:,0].str.split(': ', n=1, expand=True))
        
        return info.append(time,ignore_index = True)


    def get_link():
        link = pd.DataFrame(['Link',url]).T
        return link
    
    def get_description():
        try:
            notes = page_content.find('section', class_='description').get_text()
            return pd.DataFrame(['Description', notes.replace('\n','').strip().split('\r')[0]]).T
        except AttributeError:
            print('There is no description')
            return pd.DataFrame()
    
    Address = get_address()
    Table = get_tables()
    Link = get_link()
    Description = get_description()

    final_table1 = pd.concat([Address, Table, Link, Description],ignore_index = True).set_index([0]).T

    return final_table1

def get_loopnet_history_tables(hist_link):   
    """
    Get all building information with the link
    ----------
    hist_link : list
        a list of Building Listing Link
    Returns
    -------
    final_table1: DataFrame
        two tables for all buildings
    """    
    global loopnet_residential_scrape_error
    loopnet_residential_scrape_error = []         
    for i in range(len(hist_link)):
        try:
            if i == 0:
                print(i, hist_link[i])
                table1 = get_loopnet_history_info(hist_link[i])
                if 'Total Building Size' in table1.columns:
                    table1.rename(columns={'Total Building Size':'Building Size'},inplace = True)
                    table1.rename(columns={'Total Land Area':'Lot Size'},inplace = True)
        
        
            else:
                print(i, hist_link[i])
                temp1 = get_loopnet_history_info(hist_link[i])
                if 'Total Building Size' in temp1.columns:
                    temp1.rename(columns={'Total Building Size':'Building Size'},inplace = True)
                    temp1.rename(columns={'Total Land Area':'Lot Size'},inplace = True)
        
        
                table1 = pd.concat([table1,temp1],ignore_index = True)
                time.sleep(10)
        except:
            loopnet_residential_scrape_error.append(hist_link[i])
            pass
    
    final_table1 = table1[table1['Address'].apply(lambda x: not bool(re.search('\$', x)))]
    
    return final_table1

def loopnet_residential_off_market_cleaner(loopnet_residential_off_market):
    loopnet_residential_off_market = loopnet_residential_off_market[['Address', 'Building Size','Cap Rate',
                                                                     'Price','Property Type', 'Property Sub-type',
                                                                     'Zip','Listing ID','Date Created',
                                                                     'Link', 'Description','No. Stories','Lot Size',
                                                                     'APN / Parcel ID','Occupancy', 'Year Built',
                                                                     'Building Class','Gross Rent Multiplier']]
    
    
    loopnet_residential_off_market = loopnet_residential_off_market[loopnet_residential_off_market['Property Type'] == 'Multifamily']
    loopnet_residential_off_market['Address'] =  cleaner.easy_clean(loopnet_residential_off_market['Address'].str.upper())
    loopnet_residential_off_market['Zip'] = loopnet_residential_off_market['Zip'].str.split(', ',expand=True)[1]
    loopnet_residential_off_market['Zip'].replace(regex={'NY ':''},inplace=True)
    loopnet_residential_off_market['Lot Size'][52] = '12,866 SF'
    loopnet_residential_off_market['Lot Size'][81] = str(1.6*43560)
    loopnet_residential_off_market[['Building Size','Lot Size']] = loopnet_residential_off_market[['Building Size','Lot Size']].replace(regex={' SF':'',',':''})    
    loopnet_residential_off_market['Address'].replace(regex={', OZONE PARK NY':'',' PROSPECT HEIGHTS':''},inplace=True)
    loopnet_residential_off_market.rename(columns={'Building Size':'GSF','No. Stories':'# Floors','Description':'Sale Notes','Property Sub-type':'Sub-type'},inplace = True)
    loopnet_residential_off_market['Listing ID'] = loopnet_residential_off_market['Listing ID'].apply(lambda x: int(x.strip()))
    loopnet_residential_off_market['State'] = 'NY'
    return loopnet_residential_off_market


def merge(loopnet_residential_on_sale,loopnet_residential_off_market):
    loopnet_residential_on_sale =  loopnet_residential_cleaner(loopnet_residential_on_sale)
    loopnet_residential_off_market = loopnet_residential_off_market_cleaner(loopnet_residential_off_market)
    loopnet_residential_on_sale.columns = [c.upper() for c in loopnet_residential_on_sale.columns]
    loopnet_residential_off_market.columns = [c.upper() for c in loopnet_residential_off_market]
    
    for c in set(loopnet_residential_on_sale.columns)&set(loopnet_residential_off_market.columns):
        print(c,loopnet_residential_off_market[c].dtypes, loopnet_residential_on_sale[c].dtypes)
        try:
            if loopnet_residential_on_sale[c].dtypes == 'float64':
                loopnet_residential_off_market[c] = loopnet_residential_off_market[c].astype('float')
            elif loopnet_residential_on_sale[c].dtypes == 'object':
                loopnet_residential_off_market[c] = loopnet_residential_off_market[c].astype('str')
        except:
            pass

    ny_residential = loopnet_residential_on_sale.merge(loopnet_residential_off_market,on = list(set(loopnet_residential_on_sale.columns)&set(loopnet_residential_off_market.columns)), how = 'outer')
    ny_residential['SOLD'] = np.where(ny_residential['PRICE'].isna(),'1','0')
    ny_residential.to_csv('NY Residential.csv')
    return ny_residential

################################### Scraping Tables ####################################
# on sale scraping
#link = get_loopnet_id()
#link = list(set(link))
#loopnet_residential_on_sale = get_tables(link)
'''
loopnet_residential_on_sale = pd.read_csv('loopnet_residential 2019-08-02.csv',index_col=0)
loopnet_residential_off_market = pd.read_csv('loopnet_residential_off_market.csv',index_col=0)
loopnet_residential_on_sale = loopnet_residential_cleaner(loopnet_residential_on_sale)
'''

def get_sale_off_market_main():
    hist_link = get_loopnet_history_id()
    hist_link = list(set(hist_link))
    loopnet_residential_off_market = get_loopnet_history_tables(hist_link)
    loopnet_residential_off_market.to_csv('../../data/sample/'+'111.csv')
    loopnet_residential_off_market = loopnet_residential_off_market_cleaner(loopnet_residential_off_market)
    loopnet_residential_off_market.columns = [c.upper() for c in loopnet_residential_off_market]
    
    return loopnet_residential_off_market

# on sale and off market residential building dataframe
#ny_residential = merge(loopnet_residential_on_sale,loopnet_residential_off_market)


if __name__ == '__main__':
    df = get_sale_off_market_main()
    df.to_csv('../../data/sample/loopnet.csv')
