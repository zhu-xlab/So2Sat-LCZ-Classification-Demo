# -*- coding: utf-8 -*-
"""
Created on Mon Jul 02 09:06:08 2018
@author: hu
"""
# Last modified: 03.07.2018 19:55:14 Yuanyuan Wang
# add different OK filenames

# Last modified: 09.07.2018 12:02:00 Jingliang Hu
# read EPSG code from tiff file by the updated function se1Processing_uil.getTiffExtent

import se1Processing_uil as plee
import logging
import sys
from time import strftime
import os

# getting the arguments
dataPath = sys.argv[1]
template = sys.argv[2]
geoInfoFile = sys.argv[3]


settings = template.split('/')[-1]
# procFlag indicates the datatype of produced data: 1, unfiltered data; 2, LEE filtered data; 3, ocean water mask; 4, unfiltered high resolution data; 5 nlm filtered high resolution data
resolution = 10
if 'unfilt' in settings:
    procFlag = 1
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_UNFILT", level=logging.ERROR)
    ok_filename = "OK.mosaic_unfilt"
elif 'lee' in settings:
    procFlag = 2
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_LEEFILT", level=logging.ERROR)
    ok_filename = "OK.mosaic_lee"
elif 'water' in settings:
    procFlag = 3
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_WATERMASK", level=logging.ERROR)
    ok_filename = "OK.mosaic_water"
elif ('TC' in settings) and ('nlm' not in settings):
    procFlag = 4
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_UNFILT_HIGHRES", level=logging.ERROR)
    ok_filename = "OK.mosaic_unfilt_highres"
    resolution = 3

elif 'nlmTC' in settings:
    procFlag = 5
    logging.basicConfig(filename=dataPath+"/log.SEN1_PREPROC_NLM_HIGHRES", level=logging.ERROR)
    ok_filename = "OK.mosaic_nlm_highres"
    resolution = 3





logger = logging.getLogger().setLevel(logging.INFO)


# geoInfoFlag indicate the datatype of ROI provider: 1, GEOTIFF file; 2, KML file
if 'TIFF' in settings:
    geoInfoFlag = 1
elif 'KML' in settings:
    geoInfoFlag = 2
else:
    geoInfoFlag = 1



city = dataPath.split('/')[-1]    
pathTimes = plee.getPathOfTime(dataPath)

if geoInfoFlag == 1:
    # geotiff
    xmin,xmax,ymin,ymax,utmEPSG = plee.getTiffExtent(dataPath,geoInfoFile)
    extent = [xmin-1000,xmax+1000,ymin-1000,ymax+1000]
elif geoInfoFlag == 2:
    # kml
    points = plee.getROIPoints(dataPath,geoInfoFile)
    points,utmEPSG,_ = plee.roiLatlon2UTM(points)
    xmin = points[1,0]
    xmax = points[2,0]
    ymin = points[2,1]
    ymax = points[1,1]
    extent = [xmin,xmax,ymin,ymax]
else:
    logging.error("   ")
    logging.error("##################################################### ")
    logging.error("ERROR:  By far, ROI can only be given by KML and GEOTIFF file ")
    logging.error("##################################################### ")
    logging.error("   ")
    exit(1)

 
# loop goes over time of a city
for idxTime in range(0,len(pathTimes)):
    time = pathTimes[idxTime].split('/')[-1]
    zipPath = plee.getPath2Data(pathTimes[idxTime])
           
    # mosaic operation
    logging.info("   ")
    logging.info("#############################################################")
    logging.info("INFO: Data of the city: "+city)
    logging.info("INFO: Data of the time: "+time)
    logging.info("INFO: Operation starts at: "+strftime("%d.%m.%Y %H:%M:%S"))
    logging.info("INFO: On mosaicing operation") 
    
    # mosaic data if necessary
    flag = plee.gdalMosaic(zipPath, procFlag, utmEPSG, extent, resolution)
    
    #print flag 
    # logging
    if type(flag) is not int:
        logging.info("INFO: Operation ends at: "+strftime("%d.%m.%Y %H:%M:%S"))
        logging.info('INFO: mosaicing command:')
        logging.info('   '+' '.join(flag[:]))
        logging.info("#############################################################")
        logging.info("   ")
        os.system("printf '%s' \"0\" > "+ok_filename)
    elif flag == 3:
        logging.info('INFO: Do not need mosaicing')
        logging.info("#############################################################")
        logging.info("   ")
        if not os.path.isfile(ok_filename):
            os.system("printf '%s' \"0\" > "+ok_filename)

    elif flag == 2:
        logging.info('INFO: Mosaicing already done')
        logging.info("INFO: Operation ends at: "+strftime("%d.%m.%Y %H:%M:%S"))
        logging.info("INFO: #############################################################")
        logging.info("   ")
        if not os.path.isfile(ok_filename):
            os.system("printf '%s' \"0\" > "+ok_filename)

    elif flag == 1:
        logging.error('ERROR:   !!!!!! ERROR !!!!!!')
        logging.error("#############################################################")
        logging.error("  ")
        exit(1)

