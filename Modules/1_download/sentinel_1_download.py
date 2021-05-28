# DLR-TUM SiPEO TEAM
# So2Sat Project
# Sentinel-1 data sets download prototype
# PhD Candidate: Jingliang Hu
# Email: jingliang.hu@dlr.de
# 19.12.2017
# modified by jingling in 05.2021

import sys
import os
import download_lib as d_lib
import glob
import time
from shapely.wkt import loads
from osgeo import ogr,osr,gdal
import pandas as pd
from sentinelsat.sentinel import SentinelAPI
import sentinelsat
import xml.etree.ElementTree as ET
import pandas as pd


###############################################################################
# the link to sentinel data hub, user account and password
url = 'https://scihub.copernicus.eu/dhus'
# HERE PUT IN YOUR USER ACCOUNT
username ='sipeo_so2sat_demo'
# YOUR PASSWORK
password='sipeo_so2sat'
###############################################################################


###############################################################################
# Parameter setting
# An ROI example. A kml file contains ROI of 1692 cities whose population are larger than 300,000 in 2015
cityrois = '../../data/ROI/UN_city_list_rect_buff.kml'
# example city Lagos (One of the 1692 cities in the kml file). 
# [population ranking]_[city ID]_[city name]
cityname = ["00017_22007_Lagos", "00042_20480_Chengdu"]

# Time period
# Search data in three time periods: 
# 2017-03-01 to 2017-03-31; 2017-06-01 to 2017-06-30; and 2017-09-01 to 2017-09-30
# startDate = ["20170301","20170601","20170901"]
# endDate   = ["20170331","20170630","20170930"]
startDate = ["20210501"]
endDate   = ["20210528"]

# directory of data to be saved
outdir = '../../data/Sentinel-1/'
###############################################################################




# Load the city list and the ROIs
city_info = []
tree = ET.parse(cityrois)
root = tree.getroot()
folder = root[0][1]
for i in range(1,len(folder)):
    city_info.append([folder[i][1][0][3].text, folder[i][1][0][0].text, folder[i][1][0][1].text, folder[i][1][0][2].text, folder[i][1][0][4].text, folder[i][2][0][0][0].text])

# loop over cities
for idx_city in range(len(cityname)):
    '''
    Load the roi of the target city
    One can also modify the ROI by setting the variable "coordinate"
    '''
    city = cityname[idx_city]
    for loc in range(0,len(city_info)):
        if city_info[loc][0] == city.split('_')[1]:
            break
    loc_tmp = city_info[loc][5].split(' ')
    lon = []
    lat = []
    for loc_item in loc_tmp:
        tmp = loc_item.split(',')
        lon.append(float(tmp[0]))
        lat.append(float(tmp[1]))
    coordinate = [min(lon),max(lon),min(lat),max(lat)]
    footprint, roiPolygon = d_lib.roi_footprint(coordinate)
    # footprint, roiPolygon = d_lib.roi_buffer_footprint(coordinate) # buffered roi


    '''
    Loop over different time period 
    '''
    for tt in range(len(startDate)):
        print('\n{} in {}'.format(city, startDate[tt][:6]))
        '''
        *** DO NOT CHANGE ***
        Set up folders for data storage
        This folder structure is relevant to followup processing, e.g. data preprocessing
        '''
        outdatapath = outdir + '/' + city + '/original_dat'+'/'+startDate[tt][:6]+'/'
        if not os.path.exists(outdatapath):
            os.makedirs(outdatapath)




        '''
        Retrieve meta information
        '''
        api = SentinelAPI(username, password, url)        
        print('querying')
        products = api.query(
                            footprint,
                            beginposition=(startDate[tt],endDate[tt]),                  
                            endposition=(startDate[tt], endDate[tt]),                    
                            platformname='Sentinel-1',
                            producttype='SLC',
                            sensoroperationalmode='IW',
                            polarisationmode='VV VH'
                            )
        if len(products)==0:        
            print('INFO: {} in {}: no data found at all, change time period'.format(city, startDate[tt][:6]))
            continue
        else:
            print('INFO: {} in {}: {} data sets found'.format(city, startDate[tt][:6],len(products)))


        '''
        Find one or more data that cover the ROI
        '''
        # Meta information of searched S1 tiles       
        products_df  = api.to_dataframe(products)
        del api
        # find single tile contains the roi region
        product_tbd = d_lib.single_data_cover_roi_loopin(products_df, roiPolygon)
        # if no single tile covering the roi is found, try multiple tiles of the save orbit 
        if isinstance(product_tbd,int):
            product_tbd = d_lib.multiple_data_of_same_orbit_cover_roi(products_df, footprint)
            # if tiles of the same orbit can not cover the roi, try tiles of the same orbit direction
            if isinstance(product_tbd,int):
                product_tbd = d_lib.multiple_data_of_same_direction_cover_roi(products_df, footprint)

        # If no data or data combination cover the roi, skip the city for the time period
        if isinstance(product_tbd,int):
            print('INFO: no data for {} in {} covers the roi'.format(city, startDate[tt][:6]))
            continue
        elif len(product_tbd.shape)==1:
            print('INFO: need 1 tile in {} to cover {}.'.format(startDate[tt][:6], city))
        elif len(product_tbd.shape)==2:
            print('INFO: need {} tile in {} to cover {}.'.format(product_tbd.shape[0], startDate[tt][:6], city))


        '''
        Data downloading
        '''
        # if data to be downloaded are not online ready, wait 20 min to try again.
        secs = 1200
        if len(product_tbd.shape)==1: # only one data to be download
            check_point_file = outdatapath+product_tbd['title']+'_data_downloaded.ok'
            if os.path.exists(check_point_file):
                print('INFO: already downloaded. {}'.format(product_tbd['title']))
            while not os.path.exists(check_point_file):
                download_info = d_lib.run_download(product_tbd, outdatapath, username, password)
                if not os.path.exists(check_point_file):
                    # pause the programme to avoid the ERROR: "429 Too Many Requests"
                    print('INFO: pause {} secs to avoid ERROR429'.format(secs))
                    time.sleep(secs)
        elif len(product_tbd.shape)==2: # multiple data to be download
            for idx_md in range(product_tbd.shape[0]):
                check_point_file = outdatapath+product_tbd.iloc[idx_md]['title']+'_data_downloaded.ok'
                if os.path.exists(check_point_file):
                    print('INFO: already downloaded. {}'.format(product_tbd.iloc[idx_md]['title']))
                while not os.path.exists(check_point_file):
                    download_info = d_lib.run_download(product_tbd.iloc[idx_md], outdatapath, username, password)
                    if not os.path.exists(check_point_file):
                        # pause the programme to avoid the ERROR: "429 Too Many Requests"
                        print('INFO: pause {} secs to avoid ERROR429'.format(secs))
                        time.sleep(secs)
        else:
            print('ERROR: something wrong with the meta info of data to be downloaded')















