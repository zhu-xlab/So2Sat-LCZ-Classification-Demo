# -*- coding: utf-8 -*-
"""
Created on Tue Jun 16 09:06:08 2018
@author: hu
"""

# Last modified: 29.06.2018 23:26:12 Yuanyuan Wang
# some modification in logging
# added different filenames of the OK files for different processing 


import se1Processing_uil as plee
import logging
import sys
from time import strftime
import os


# getting the arguments
dataPath = sys.argv[1]
template = sys.argv[2]

#kmlCityList = sys.argv[3]
# directory to all lcz42 label folder or to the kml city list
geoInfoFile = sys.argv[3]

settings = template.split('/')[-1]


# procFlag indicates the datatype of produced data: 1, unfiltered data; 2, LEE filtered data; 3, ocean water mask
if 'unfilt' in settings:
    procFlag = 1
elif 'lee' in settings:
    procFlag = 2
elif 'water' in settings:
    procFlag = 3

# projFlag indicates the projection of produced data: 1, in WGS84 longitude and latitude; 2, in UTM system
if 'WGS' in settings:
    projFlag = 1
elif 'UTM' in settings:
    projFlag = 2

# geoInfoFlag indicate the datatype of ROI provider: 1, GEOTIFF file; 2, KML file
if 'TIFF' in settings:
    geoInfoFlag = 1
elif 'KML' in settings:
    geoInfoFlag = 2



print('procFlag: '+str(procFlag))
print('projFlag: '+str(projFlag))
print('geoInfoFlag: '+str(geoInfoFlag))


# initial logger file
if procFlag==1:
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_UNFILT", level=logging.ERROR)
    ok_filename = "OK.geocoding_unfilt"
elif procFlag==2:
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_LEEFILT", level=logging.ERROR)
    ok_filename = "OK.geocoding_lee"
elif procFlag==3:
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_WATERMASK", level=logging.ERROR)
    ok_filename = "OK.geocoding_water"

logger = logging.getLogger().setLevel(logging.INFO)


# get data path
city = dataPath.split('/')[-1]    
pathTimes = plee.getPathOfTime(dataPath)

# get the extent of city ROI in coordinate
# get the extent of city ROI in pixel
# get the projection data of data
if geoInfoFlag == 1:
    # geotiff
    geoRegion = plee.getGeoRegionTiff(dataPath,geoInfoFile)
    region = plee.getRegionTiff(dataPath,geoInfoFile)
elif geoInfoFlag == 2:
    # kml
    geoRegion,centerPoint = plee.getGeoRegion(dataPath,geoInfoFile) 
    region = plee.getRegion(dataPath,geoInfoFile)     
else:
    logging.error("   ")
    logging.error(" ##################################################### ")
    logging.error(" #FATAL: By far, ROI can only be given by KML and GEOTIFF file ")
    logging.error(" ##################################################### ")
    logging.error("   ")    


if projFlag == 1:
    # gpt takes care of WGS84 projection automatically
    projection = 0 
elif projFlag == 2:
    # read UTM prjection from tiff file
    if geoInfoFlag == 1:
        projection = plee.getProjTiff(dataPath,geoInfoFile)

    # read WGS84 projection from kml file, and convert to UTM
    elif geoInfoFlag == 2:
        _,projection = plee.latlon2utm(centerPoint)        

else:
    logging.error("   ")
    logging.error(" ######################################################################## ")
    logging.error(" #FATAL: By far, Projection can only be given as UTM and WGS84 longitude latitude ")
    logging.error(" ######################################################################## ")
    logging.error("   ")



# loop goes over time of a city
for idxTime in range(0,len(pathTimes)):
    time = pathTimes[idxTime].split('/')[-1]
    zipPath = plee.getPath2Data(pathTimes[idxTime])
    
    # loop goes over data of a city at a time
    for idxData in range(0,len(zipPath)):            
        # start preprocessing
        # logging
        logging.info("   ")
        logging.info("   #############################################################")
        logging.info("   Data of the city: "+city)
        logging.info("   Data of the time: "+time)
        logging.info("   Total "+str(len(zipPath))+" data sets, processing on data: "+str(idxData+1))
        logging.info("   Operation starts at: "+strftime("%d.%m.%Y %H:%M:%S"))
        if procFlag==1:
            logging.info("   apply orbit file, calibration, deburst, terrain correction, subset: ")
        elif procFlag==2:
            logging.info("   apply orbit file, calibration, deburst, Lee filtering, terrain correction, subset: ")
        elif procFlag==3:
            logging.info("   apply orbit file, calibration, deburst, filtering, terrain correction, subset: ")


        # processing
        flag, outputData = plee.createGPTTemplate(zipPath[idxData], template, geoRegion, region, procFlag, projFlag, projection)
        # logging
        print("Test done")
        if flag == 1:
            logging.info("   Operation ends at: "+strftime("%d.%m.%Y %H:%M:%S"))
            logging.info('   process done')
            logging.info("   #############################################################")
            logging.info("      ")
            os.system("printf '%s' \"0\" > " + ok_filename)
        elif flag == 2:
            logging.info('   already done')
            logging.info("   #############################################################")
            logging.info("      ")
            if not os.path.isfile(ok_filename):
                os.system("printf '%s' \"0\" > " + ok_filename)
        elif flag == 0:
            logging.error('  !!!!!! ERROR: gpt path was not configured !!!!!!')
            logging.error("  #############################################################")
            logging.error("  ")

