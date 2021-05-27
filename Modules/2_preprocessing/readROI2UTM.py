#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : ../util/readROI2UTM.py
# Author            : Jingliang Hu
# Date              : 09.07.2018 10:05:44
# Last Modified Date: 09.07.2018 10:05:44
# Last Modified By  : Yuanyuan Wang <y.wang@tum.de>

# Last modified: Chunping Qiu
# adapted for SEN2 

# Last modified: 09.07.2018 10:06:10 Yuanyuan Wang
# changed ROI file as an input, instead of hard coded 

from osgeo import ogr,osr,gdal
import numpy as np
import xml.etree.ElementTree as et
import sys,os


def getROIPoints(cpath,kmlCityList):
    # This function finds the WGS coordinates of ROI for one city
    # Input
    #       -- cpath        - path to the file of city, where data saved
    #       -- kmlCityList  - path to the ROI kml file
    #
    # Output
    #       -- points       - a 3 by 2 array,
    #                       - 1st column is longitude, 2nd column is latitude
    #                       - 1st row: center point, 2nd row: upper-left cornor, 3rd row: bottom-right cornor

    # read the unique index of city
    temp = cpath.split('/')[-1].split('_')
    # print cpath
    # print temp
    idx = int(temp[1])

    # find the ROI coordinate of the city
    tree = et.parse(kmlCityList)
    for item in tree.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        if item[1][0][3].text == str(idx):
            found = item
            break

    coordText = found[2][0][0][0].text
    temp = coordText.split(' ')
    x = np.zeros([5,1])
    y = np.zeros([5,1])
    for i in range(0,len(temp)):
        a,b = temp[i].split(',')
        x[i] = np.double(a)
        y[i] = np.double(b)

    xmin = np.min(x)
    xmax = np.max(x)
    ymin = np.min(y)
    ymax = np.max(y)

    points = np.array([[np.float32(xmin+xmax)/2,np.float32(ymin+ymax)/2],[xmin,ymax],[xmax,ymin]])
    return points



def roiLatlon2UTM(WGSPoint):
    # This function transfers geographical coordinate (lon-lat) into WGS 84 / UTM zone coordinate using GDAL
    # Input:
    #       -- WGSPoint       - A N by M array of lon-lat coordinate; N is number of points, 1st col is longitude, 2nd col is latitude
    #
    # Output:
    #       -- UTMPoints      - A N by M array of WGS 84 /UTM zone coordinate; N is number of points, 1st col is X, 2nd col is Y
    #

    WGSPoint = np.array(WGSPoint)

    if len(WGSPoint.shape)==1:
        WGSPoint = np.stack((WGSPoint,WGSPoint),axis=0)
        nb,dim = np.shape(WGSPoint)
    elif len(WGSPoint.shape)==2:
        # number of WGSPoint
        nb,dim = np.shape(WGSPoint)

    elif len(WGSPoint.shape)==3:
        print('ERROR: DIMENSION OF POINTS SHOULD NO MORE THAN TWO')

    # geographic coordinate (lat-lon) WGS84
    inputEPSG = 4326
    # WGS 84 / UTM zone
    if WGSPoint[0][1]<0:
        outputEPSG = 32700
    else:
        outputEPSG = 32600

    outputEPSG = int(outputEPSG + np.floor((WGSPoint[0][0]+180)/6) + 1)

    # create coordinate transformation
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(inputEPSG)

    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)

    utmProjInfo = outSpatialRef.ExportToWkt()

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

    # transform point
    UTMPoints = np.zeros(WGSPoint.shape)
    for i in range(0,np.size(WGSPoint,axis=0)):
        p = ogr.Geometry(ogr.wkbPoint)
        p.AddPoint(WGSPoint[i][0], WGSPoint[i][1])
        p.Transform(coordTransform)
        UTMPoints[i][0] = p.GetX()
        UTMPoints[i][1] = p.GetY()


    return UTMPoints, utmProjInfo

# path2City = '/datastore/DATA/classification/SEN2/global_processing/01690_22878_Southend-On-Sea'
# path2KML = '/datastore/DATA/classification/AUXDATA/UN_city_list_rect.kml'

path2City = sys.argv[1]
path2KML = sys.argv[2]
# print(sys.argv[0])
# print(sys.argv[1])
# print(len(sys.argv))

wgsPoints = getROIPoints(path2City,path2KML)
#print(wgsPoints)

utmPoints, utmProjInfo = roiLatlon2UTM(wgsPoints)
#print(utmPoints)
print(utmProjInfo)
