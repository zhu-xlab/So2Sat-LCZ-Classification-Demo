# DLR-TUM SiPEO TEAM
# So2Sat Project
# Sentinel-1 data sets download prototype
# PhD Candidate: Jingliang Hu
# Email: jingliang.hu@dlr.de
# 19.12.2017

import os
import logging
import glob
from shapely.wkt import loads
from osgeo import ogr,osr,gdal
import pandas as pd
from sentinelsat.sentinel import SentinelAPI
import sentinelsat
print(sentinelsat.__file__)



###############################################################################
# the link to sentinel data hub, user account and password
url = 'https://scihub.copernicus.eu/dhus'
# HERE PUT IN YOUR USER ACCOUNT
username ='sipeo_so2sat_demo'
# YOUR PASSWORK
password='sipeo_so2sat'
###############################################################################


###############################################################################
# parameter setting

# directory to a file, which stores roi.kml or geotiff files of all cities
# file structure: 'cityrois'/city/city_roi.kml. e.g. 'cityrois/zurich/zurich_roi.kml'
cityrois = '../../data/ROI'
# set the type of ROI file
# roiType = 'geotiff' 
roiType = 'kml' 

# time requirement
# startDate = ["20170301","20170601","20170901"]
# endDate   = ["20170331","20170630","20170930"]
startDate = ["20200601"]
endDate   = ["20200731"]


# directory of data to be saved
outdir = '../../data/Sentinel-1/'

logging.basicConfig(filename=outdir+"/sentinel_1_download.log", level=logging.INFO)
###############################################################################






# # get the city list
cityname = glob.glob(cityrois+"/*")

# cityname = 'sao_paulo'

# loop over cities
for city in cityname:
    roi_path = city
    city = city.split("/")[-1].split(".")[0]
    ###############################################################################
    #
    #               read the region of interested ROI
    #

    if roiType.lower() == 'kml':
        # directory to the ROI.kml file
        kmlpath = roi_path
        # read footprint from roi kml for data searching
        driver = ogr.GetDriverByName('kml')
        kml = driver.Open(kmlpath)
        kmllayer = kml.GetLayer();
        coordinate = kmllayer.GetExtent()
    elif roiType.lower()=='geotiff':
        # directory to the ROI.kml file
        tifpath = roi_path
        tifdat = gdal.Open(tifpath)
        ulx, xres, xskew, uly, yskew, yres  = tifdat.GetGeoTransform()
        lrx = ulx + (tifdat.RasterXSize * xres)
        lry = uly + (tifdat.RasterYSize * yres)
        # Setup the source projection - you can also import from epsg, proj4...
        source = osr.SpatialReference()
        source.ImportFromWkt(tifdat.GetProjection())
        # The target wgs84/lonlat projection
        target = osr.SpatialReference()
        target.ImportFromEPSG(4326)
        # Create the transform - this can be used repeatedly
        transform = osr.CoordinateTransformation(source, target)
        # Transform the point. You can also create an ogr geometry and use the more generic `point.Transform()`
        ul = transform.TransformPoint(ulx, uly)
        lr = transform.TransformPoint(lrx, lry)
        # ROI coordinates in WGS84/lonlat
        coordinate = [ul[0],lr[0],lr[1],ul[1]]
    else:
        print('----------------- Wrong given ROI data type, only KML and GEOTIFF for now  ---------------------\n')
        logging.info('----------------- Wrong given ROI data type, only KML and GEOTIFF for now  ---------------------\n')
        break

    x_buffer = (coordinate[1]-coordinate[0])/10
    y_buffer = (coordinate[3]-coordinate[2])/10
    xmin = coordinate[0] - x_buffer
    xmax = coordinate[1] + x_buffer
    ymin = coordinate[2] - y_buffer
    ymax = coordinate[3] + y_buffer

    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xmin,ymin)
    ring.AddPoint(xmax,ymin)
    ring.AddPoint(xmax,ymax)
    ring.AddPoint(xmin,ymax)
    ring.AddPoint(xmin,ymin)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    footprint = poly.ExportToWkt()
    roiPolygon = loads(footprint)
    ###############################################################################    
    
    for tt in range(0,len(startDate)):
        print('\n------------------- searching and downloading data sets of '+city+' in '+startDate[tt][:6]+' -------------------------\n')
        logging.info('\n------------------- searching and downloading data sets of '+city+' in '+startDate[tt][:6]+' -------------------------\n')
        ###############################################################################
        # path setting (do not change)    
        outdatapath = outdir + '/' + city + '/original_dat'+'/'+startDate[tt][:6]+'/'
        
        ###############################################################################
        #
        #               aquire the meta data of overlapped data sets
        #
        # part one
        # query the data in region of interested
        api = SentinelAPI(username, password, url)
        
        print('querying\n')
        logging.info('querying\n')
        products = api.query(
                            footprint,
                            beginposition=(startDate[tt],endDate[tt]),                  
                            endposition=(startDate[tt], endDate[tt]),                    
                            platformname='Sentinel-1',
                            producttype='SLC',
                            sensoroperationalmode='IW',
                            polarisationmode='VV VH'
                            )
        
        print(len(products))
        logging.info(len(products))
        if len(products)==0:        
            print('----------------- '+city+' in '+startDate[tt][:6]+': no data set was found at all, change time period ---------------------\n')
            logging.info('----------------- '+city+' in '+startDate[tt][:6]+': no data set was found at all, change time period ---------------------\n')
            continue
        
        # save searched meta information into a data frame        
        products_df  = api.to_dataframe(products)

        # initial a dataframe to store the meta data of target data sets
        targetData = pd.DataFrame()

        # found == True when suitable data set found, otherwise False
        found = False
        
        ###############################################################################
        # only consider descending orbit data first
        product_sort = products_df.drop(products_df[products_df.orbitdirection == 'ASCENDING'].index)

        ###############################################################################
        # download desending orbit data if availbe    
        if not product_sort.empty:
            ###############################################################################
            #
            #               search whether one data set cover the whole ROI
            #
            product_sort = product_sort.sort_values(['beginposition'],ascending = [True])
            # loop the searched scenes 
            for index, row in product_sort.iterrows():
                scenePolygon = loads(row['footprint'])
                if scenePolygon.contains(roiPolygon):
                    targetData = targetData.append(row)
                    found = True
                    break
            ###############################################################################
        
            ###############################################################################
            #
            # No single data set covers the whole ROI, go for multiple data sets which on the same orbit
            #
            if found == False:                
                for index, row in product_sort.iterrows():
                    orbitData = product_sort[product_sort.orbitnumber == row.orbitnumber]
                    scenePolygon = loads(row['footprint'])
                    targetData = pd.DataFrame()
                    targetData = targetData.append(row)
                    for idx, rw in orbitData.iterrows():
                        sceneadd = loads(rw['footprint'])
                        if targetData.iloc[0]['uuid']!=rw['uuid']:
                            targetData = targetData.append(rw)
                            scenePolygon = scenePolygon.union(sceneadd)
                        if scenePolygon.contains(roiPolygon):
                            found = True
                            break
                    if found:
                        break
            ###############################################################################
            
            
            ###############################################################################
            #
            # No multiple data sets on the same orbit cover the whole ROI, 
            # go for multiple data sets which are not on the save orbit
            #
            if found == False:
                scenePolygon = loads(product_sort.iloc[0]['footprint'])
                targetData = targetData.append(product_sort.iloc[0])
                
                # find data sets sorted by time regardless of orbit
                for index, row in product_sort.iterrows():
                    sceneadd = loads(row['footprint'])
                    if targetData.iloc[0]['uuid']!=row['uuid']:
                        targetData = targetData.append(row)
                        scenePolygon = scenePolygon.union(sceneadd)
                    if scenePolygon.contains(roiPolygon):
                        found = True
                        break                
                # goes through the found target data sets to eliminate redundent data
                if found:
                    print(str(targetData.shape[0])+" data sets found, which cross orbits")
                    logging.info(str(targetData.shape[0])+" data sets found, which cross orbits")
                    temp = targetData
                    for index,row in targetData.iterrows():
                        temp = temp.drop(temp[temp.uuid == row.uuid].index)
                        scenePolygon = loads(temp.iloc[0]['footprint'])
                        for idx,rw in temp.iterrows():
                            sceneadd = loads(rw['footprint'])
                            scenePolygon = scenePolygon.union(sceneadd)
                        if scenePolygon.contains(roiPolygon)==False:
                            temp = temp.append(row)
                            
                    print(str(targetData.shape[0]-temp.shape[0])+" redundent data sets eleminated")
                    logging.info(str(targetData.shape[0]-temp.shape[0])+" redundent data sets eleminated")
                    targetData = pd.DataFrame()
                    targetData = targetData.append(temp)
                else:
                    # all searched data sets would not cover the roi
                    targetData = pd.DataFrame()
            ###############################################################################
            
        # no descending orbit data availble or suits the criterion, consider only acsending orbit data 
        product_sort_ascend = products_df.drop(products_df[products_df.orbitdirection == 'DESCENDING'].index)
       
        ###############################################################################        
        # if no descending data availbe or no descending data suit demand, go for ascending data
        if (product_sort.empty or not found) and (not product_sort_ascend.empty):
            ###############################################################################
            #
            #               search whether one data set cover the whole ROI
            #
            product_sort_ascend = product_sort_ascend.sort_values(['beginposition'],ascending = [True])
            # loop the searched scenes 
            for index, row in product_sort_ascend.iterrows():
                scenePolygon = loads(row['footprint'])
                if scenePolygon.contains(roiPolygon):
                    targetData = targetData.append(row)
                    found = True
                    break
            ###############################################################################
        
            ###############################################################################
            #
            # No single data set covers the whole ROI, go for multiple data sets which on the same orbit
            #
            if found == False:                
                for index, row in product_sort_ascend.iterrows():
                    orbitData = product_sort_ascend[product_sort_ascend.orbitnumber == row.orbitnumber]
                    scenePolygon = loads(row['footprint'])
                    targetData = pd.DataFrame()
                    targetData = targetData.append(row)
                    for idx, rw in orbitData.iterrows():
                        sceneadd = loads(rw['footprint'])
                        if targetData.iloc[0]['uuid']!=rw['uuid']:
                            targetData = targetData.append(rw)
                            scenePolygon = scenePolygon.union(sceneadd)
                        if scenePolygon.contains(roiPolygon):
                            found = True
                            break
                    if found:
                        break
                    else:
                        targetData = pd.DataFrame()
            ###############################################################################
            
            
            ###############################################################################
            #
            # No multiple data sets on the same orbit cover the whole ROI, 
            # go for multiple data sets which are not on the save orbit
            #
            if found == False:
                scenePolygon = loads(product_sort_ascend.iloc[0]['footprint'])
                targetData = targetData.append(product_sort_ascend.iloc[0])
                
                # find data sets sorted by time regardless of orbit
                for index, row in product_sort_ascend.iterrows():
                    sceneadd = loads(row['footprint'])
                    if targetData.iloc[0]['uuid']!=row['uuid']:
                        targetData = targetData.append(row)
                        scenePolygon = scenePolygon.union(sceneadd)
                    if scenePolygon.contains(roiPolygon):
                        found = True
                        break
                print(str(targetData.shape[0])+" data sets found, which cross orbits")
                logging.info(str(targetData.shape[0])+" data sets found, which cross orbits")
                             
                
                # goes through the found target data sets to eliminate redundent data
                if found:
                    temp = targetData
                    for index,row in targetData.iterrows():
                        temp = temp.drop(temp[temp.uuid == row.uuid].index)
                        scenePolygon = loads(temp.iloc[0]['footprint'])
                        for idx,rw in temp.iterrows():
                            sceneadd = loads(rw['footprint'])
                            scenePolygon = scenePolygon.union(sceneadd)
                        if scenePolygon.contains(roiPolygon)==False:
                            temp = temp.append(row)
                            
                    print(str(targetData.shape[0]-temp.shape[0])+" redundent data sets eleminated")
                    logging.info(str(targetData.shape[0]-temp.shape[0])+" redundent data sets eleminated")
                                      
                    targetData = pd.DataFrame()
                    targetData = targetData.append(temp)
                else:
                    targetData = pd.DataFrame()
            ###############################################################################
            
                
        
        
        ###############################################################################
        #
        #                              Start downloading
        #
        if targetData.empty:
            print(city)
            print(startDate[tt][:6])

            print('----------------- '+city+' in '+startDate[tt][:6]+': no data set covering the whole ROI was found, change time period ---------------------' )
            logging.info('----------------- '+city+' in '+startDate[tt][:6]+': no data set covering the whole ROI was found, change time period ---------------------')
        elif targetData.shape[0]==1:
            if os.path.exists(outdatapath)==False:
                os.makedirs(outdatapath)
            print('----------------- '+city+' in '+startDate[tt][:6]+': one data set covering the whole ROI was found ---------------------')
            logging.info('----------------- '+city+' in '+startDate[tt][:6]+': one data set covering the whole ROI was found ---------------------')

            targetData
            print('orbit direction: '+ targetData['orbitdirection'][0])
            logging.info('orbit direction: '+ targetData['orbitdirection'][0])
            try:
                api.download(targetData.iloc[0]['uuid'], directory_path=outdatapath)
            except Exception:
                api.download(targetData.loc['uuid'], directory_path=outdatapath)

            print ('----------------- '+city+' in '+startDate[tt][:6]+' downloaded ---------------------')
            logging.info('----------------- '+city+' in '+startDate[tt][:6]+' downloaded ---------------------')
        elif targetData.shape[0] > 1:
            if os.path.exists(outdatapath)==False:
                os.makedirs(outdatapath)
            print ('----------------- '+city+' in '+startDate[tt][:6]+': '+str(targetData.shape[0])+' data sets combined covering the whole ROI was found ---------------------')
            logging.info('----------------- '+city+' in '+startDate[tt][:6]+': '+str(targetData.shape[0])+' data sets combined covering the whole ROI was found ---------------------')
            for idx, row in targetData.iterrows():
                print('orbit direction: '+ row['orbitdirection'])
                logging.info('orbit direction: '+ row['orbitdirection'])
                try:
                    api.download(row.iloc[0]['uuid'], directory_path=outdatapath)
                except Exception:
                    api.download(row.loc['uuid'], directory_path=outdatapath)

            print ('--------------------- '+city+' in '+startDate[tt][:6]+': multiple data downloaded, need mosaic ------------------------')
            logging.info('--------------------- '+city+' in '+startDate[tt][:6]+': multiple data downloaded, need mosaic ------------------------')
        else:
            print ('----------------- ERROR PLEASE CHECK ---------------------')
            logging.info('----------------- ERROR PLEASE CHECK ---------------------')

        logging.info('\n'* 5)

        ###############################################################################
        
