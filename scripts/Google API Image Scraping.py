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

class PicDownloader:

    def __init__(self):
        self.key  = "AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE"

    def searching_from_pluto(self, pluto, address, target):
        return pluto[pluto['ADDRESS'] == address][target].values[0]
        
    def download(self, url, name):
        urllib.request.urlretrieve(url.replace(" ", "%20"),"%s.png" % name)

    def gen_url(self, geom, fov=100, heading=0, pitch=30, size=(500, 500)):
        x, y = size
        lat, lng = geom
        return "https://maps.googleapis.com/maps/api/streetview?size=%s"\
                "x%s&location=%s,%s&fov=%s&heading=%s&pitch=%s"\
                "&key=AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE" \
                % (x, y, lat, lng, fov, heading, pitch)

    def gen_url_by_string(self, address, fov=60, pitch=30, size=(400, 400)):
        x, y = size
        return "https://maps.googleapis.com/maps/api/streetview?size=%sx"\
                "%s&location=%s&fov=%s&pitch=%s"\
                "&key=AIzaSyBMsupEpnbssPowczxp3ow0QPPW01TE-fE" \
                % (x, y, address, fov, pitch)

    def address_checker(self, address, pic_path, folders):

        addr_exist = False

        for folder in folders:
            if os.path.exists(f'{pic_path}/{folder}/{address}.png'):
                addr_exist = True

        return addr_exist

    def export_addr_img(self, data, pic_path, saving_dir, folders):

        city = 'PHL'
        address_list = list(set(list(data.dropna(subset=['ADDRESS'])['ADDRESS'].values)))

        for address in address_list:
            try:
                print(str(address_list.index(address)))
                new_addr = '_'.join(address.split('/')) + ', ' + city
                new_addr_pic = '_'.join(address.split('/'))
                
                addr_exist = self.address_checker(new_addr, pic_path, folders)    

                if not addr_exist and new_addr[0].isnumeric():
                    url = self.gen_url_by_string(new_addr)
                    saving_path = f'{saving_dir}/{new_addr}'
                    self.download(url, saving_path)
                    time.sleep(5)
                
            except Exception as e:
                print(e)
                print(str(address_list.index(address)))
                new_addr = '_'.join(address.split('/')) + ', ' + city
                new_addr_pic = '_'.join(address.split('/'))
                pass

if __name__ == '__main__':
    PD = PicDownloader()
    data_path = '../data/project'
    data = pd.read_csv(f'{data_path}/PLUTO_monthly_1.18.2020.csv', index_col=0)
    pic_path = '../pictures'
    saving_dir = '../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures'
    folders = ['Brick', 'Glass', 'Limestone', 'Wood Panels', 'Other']
    PD.export_addr_img(data, pic_path, saving_dir, folders)

# data_path = '../data/project'
# files_name = {}
# pluto = pd.read_csv(f'{data_path}/PHLPL-001 All_Properties [byaddress;location] PLUTO PLUTO_monthly_1.18.2020.csv', index_col = 0)
# files_name['PHL'] = ['PHLPL-001 All_Properties [byaddress;location] PLUTO PLUTO_monthly_1.18.2020.csv']

# for city in files_name.keys():
#     names = files_name[city]
#     address_list = []
#     file = ''
#     for file_name in names:
#         file = pd.read_csv(f'{data_path}/{file_name}', index_col = 0)
#         address_list.extend(list(set(list(file.dropna(subset=['ADDRESS'])['ADDRESS'].values))))
    
#     address_list = list(set(address_list))
#     folders = ['Brick', 'Glass', 'Limestone', 'Wood Panels', 'Other']
    
#     n = 0
    
#     for address in address_list[10000:]:
#         if n >= 10000:
#             break
        
#         zipcode = PD.searching_from_pluto(file, address, 'ZIP')
#         try:
#             new_addr = '_'.join(address.split('/')) + ', ' + city
#             addr_exist = PD.address_checker(new_addr, '../pictures', folders)
#             if not addr_exist:
#                 print(address_list.index(address))
#                 new_addr_pic = '_'.join(address.split('/')) + ', ' + str(zipcode)
                
#                 url = PD.gen_url_by_string(new_addr_pic)
#                 saving_path = f'../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/{new_addr}'
#                 PD.download(url, saving_path)
#                 time.sleep(5)
#                 n+=1
#         except Exception as e:
#             print(e)
#             time.sleep(15)
#             new_addr = '_'.join(address.split('/')) + ', ' + city
#             addr_exist = PD.address_checker(new_addr, '../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures', folders)
#             if not addr_exist:
#                 print(address_list.index(address))
#                 new_addr_pic = '_'.join(address.split('/')) + ', ' + str(zipcode)
                
#                 url = PD.gen_url_by_string(new_addr_pic)
#                 saving_path = f'../Whiterock Database/Pennsylvania/Philadelphia - PHL/Pictures/{new_addr}'
#                 PD.download(url, saving_path)
#                 time.sleep(5)
#                 n+=1
        
# property_for_sale = pd.read_csv(f'{data_path}/PLUTO_monthly_1.18.2020.csv', index_col=0)

# city = 'PHL'
# sale_address_list = list(set(list(property_for_sale.dropna(subset=['ADDRESS'])['ADDRESS'].values)))

# for address in sale_address_list:

#     try:
#         print(str(sale_address_list.index(address)))
#         new_addr = '_'.join(address.split('/')) + ', ' + city
#         new_addr_pic = '_'.join(address.split('/'))
        
#         addr_exist = PD.address_checker(new_addr, '../pictures', folders)    

#         if not addr_exits and new_addr[0].isnumeric():
#             url = PD.gen_url_by_string(new_addr)
#             saving_path = "../pictures"+new_addr
#             PD.download(url, saving_path)
#             time.sleep(5)
        
#     except Exception as e:
#         print(e)
#         print(str(sale_address_list.index(address)))
#         new_addr = '_'.join(address.split('/')) + ', ' + city
#         new_addr_pic = '_'.join(address.split('/'))
#         pass
        

