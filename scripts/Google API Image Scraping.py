# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 20:23:28 2019

@author: Administrator
"""

import urllib
import pandas as pd
import numpy as np
import time
import os

def searching_from_pluto(pluto, address, target):
    return pluto[pluto['ADDRESS'] == address][target].values[0]

class PicDownloader:
    def __init__(self):
        self.key  = "AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE"
        
    def download(self, url, name):
        urllib.request.urlretrieve(url.replace(" ", "%20"),"%s.png" % name)

    def gen_url(self, geom, fov=100, heading=0, pitch=30, size=(500, 500)):
        # fov控制镜头缩进，数值越小图片越大，最大为120
        # heading控制朝向，0为北，90为东，180为南
        # pitch控制向上的仰视的角度
        x, y = size
        lat, lng = geom
        return "https://maps.googleapis.com/maps/api/streetview?size=%sx%s&location=%s,%s&fov=%s&heading=%s&pitch=%s&key=AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE" % (x, y, lat, lng, fov, heading, pitch)

    def gen_url_by_string(self, address, fov=60, pitch=30, size=(400, 400)):
        x, y = size
        return "https://maps.googleapis.com/maps/api/streetview?size=%sx%s&location=%s&fov=%s&pitch=%s&key=AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE" % (x, y, address, fov, pitch)

PD = PicDownloader()

data_path = '../data/project'
files_name = {}
pluto = pd.read_csv(f'{data_path}/PHLPL-001 All_Properties [byaddress;location] PLUTO PLUTO_monthly_1.18.2020.csv', index_col = 0)
files_name['PHL'] = ['PHLPL-001 All_Properties [byaddress;location] PLUTO PLUTO_monthly_1.18.2020.csv']

for city in files_name.keys():
    names = files_name[city]
    address_list = []
    file = ''
    for file_name in names:
        file = pd.read_csv(f'{data_path}/{file_name}', index_col = 0)
        address_list.extend(list(set(list(file.dropna(subset=['ADDRESS'])['ADDRESS'].values))))
    
    address_list = list(set(address_list))
    
    n = 0
    
    for address in address_list[10000:]:
        if n >= 10000:
            break
        
        zipcode = searching_from_pluto(file, address, 'ZIP')
        try:
            new_addr = '_'.join(address.split('/')) + ', ' + city
            if not os.path.exists(f'../pictures/Brick/{new_addr}.png'):
                if not os.path.exists(f'../pictures/Glass/{new_addr}.png'):
                    if not os.path.exists(f'../pictures/Limestone/{new_addr}.png'):
                        if not os.path.exists(f'../pictures/Wood Panels/{new_addr}.png'):
                            if not os.path.exists(f'../pictures/Other/{new_addr}.png'):
                                print(address_list.index(address))
                                new_addr_pic = '_'.join(address.split('/')) + ', ' + str(zipcode)
                                
                                url = PD.gen_url_by_string(new_addr_pic)
                                saving_path = "../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/"+new_addr
                                PD.download(url, saving_path)
                                time.sleep(5)
                                n+=1
        except Exception as e:
            print(e)
            time.sleep(15)
            new_addr = '_'.join(address.split('/')) + ', ' + city
            if not os.path.exists("../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/Brick/"+new_addr+".png"):
                if not os.path.exists("../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/Glass/"+new_addr+".png"):
                    if not os.path.exists("../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/Limestone/"+new_addr+".png"):
                        if not os.path.exists("../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/Wood Panels/"+new_addr+".png"):
                            if not os.path.exists("../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/Other/"+new_addr+".png"):
                                print(address_list.index(address))
                                new_addr_pic = '_'.join(address.split('/')) + ', ' + str(zipcode)
                                
                                url = PD.gen_url_by_string(new_addr_pic)
                                saving_path = "../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/"+new_addr
                                PD.download(url, saving_path)
                                time.sleep(5)
                                n+=1
        

#%%
property_for_sale = pd.read_csv(f'{data_path}/PLUTO_monthly_1.18.2020.csv',index_col = 0)
# property_for_sale = pd.read_csv(data_path+'PHL New Sales.csv')

city = 'PHL'
sale_address_list = list(set(list(property_for_sale.dropna(subset=['ADDRESS'])['ADDRESS'].values)))

for address in sale_address_list:
    #zipcode = property_for_sale[property_for_sale['ADDRESS'] == address]['ZIP'].values[0]
    #try:
    #    zipcode = int(zipcode)
    #except:
    #    zipcode = np.nan
    #if np.isnan(zipcode):
    #    try:
    #        zipcode = int(searching_from_pluto(pluto,address,'ZIP'))
    #    except:
    #        zipcode = 0
    #zipcode = int(zipcode)   
    try:
        print(str(sale_address_list.index(address)))#+' '+str(zipcode))
        new_addr = '_'.join(address.split('/')) + ', ' + city
        new_addr_pic = '_'.join(address.split('/')) #+ ', ' + str(zipcode)
        #url = PD.gen_url_by_string(new_addr_pic)
        #saving_path = "D:/PHL/pics/"+new_addr
        #PD.download(url, saving_path)
        #time.sleep(5)
        
        if not os.path.exists("../pictures/Brick/"+new_addr+".png"):
            if not os.path.exists("../pictures/Glass/"+new_addr+".png"):
                if not os.path.exists("../pictures/Limestone/"+new_addr+".png"):
                    if not os.path.exists("../pictures/Wood Panels/"+new_addr+".png"):
                        if not os.path.exists("../pictures/Other/"+new_addr+".png"):
                            if new_addr[0].isnumeric():
                                url = PD.gen_url_by_string(new_addr)
                                saving_path = "../pictures"+new_addr
                                PD.download(url, saving_path)
                                time.sleep(5)
        
    except Exception as e:
        print(e)
        print(str(sale_address_list.index(address)))#+' '+str(zipcode))
        new_addr = '_'.join(address.split('/')) + ', ' + city
        new_addr_pic = '_'.join(address.split('/')) #+ ', ' + str(zipcode)
        #url = PD.gen_url_by_string(new_addr_pic)
        #saving_path = "D:/PHL/pics/"+new_addr
        #PD.download(url, saving_path)
        #time.sleep(5)
        pass
        

