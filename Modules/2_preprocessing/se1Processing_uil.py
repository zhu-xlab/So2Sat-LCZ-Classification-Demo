# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 15:02:49 2018

@author: jingliang, hu
"""

# Last modified: 03.07.2018 00:08:28 Yuanyuan Wang
# Improved logging and exit code  

# Last modified: 09.07.2018 12:01:00 Jingliang Hu
# update function 'getTiffExtent' to get EPSG code from tiff ROI

# Last modified: 10.07.2018 14:09:35 Yuanyuan Wang
# added multi thread in gdalwarp

import os
import glob
import subprocess
import numpy as np
import xml.etree.ElementTree as et
from osgeo import ogr,osr,gdal

unfiltStringList = ['geocoded_subset_unfilt_dat','_Orb_Cal_Deb_TC_SUB.tif','mosaic_unfilt_dat']
leefilStringList = ['geocoded_subset_dat','_Orb_Cal_Deb_Spk_TC_SUB.tif','mosaic_dat']

def createGPTTemplate(inputZip, template, geoRegion, region, procFlag, projFlag, projection=0):
    # This function updates the gpt preprocessing xml template for each downloaded data and starts the preprocessing
    # Input:
    #       -- inputZip         - downloaded sentinel-1 data in zip
    #       -- template         - path to gpt xml template
    #       -- geoRegion        - the coordinate of ROI
    #       -- region           - pixel-wise extent of ROI
    #       -- procFlag         - processing flag: 1: no filtering, 2: lee filtering, 3: water mask, 4: range azimuth complex form, 5: range azimuth covariance matrix (boxcar filtered)
    #       -- projFlag         - projection flag: 1: WGS longitude, latitude, 2: UTM
    #
    # Output:
    #       -- template         - write the updated template
    #       -- data             - save processed data
    #
    # Example input:
    #       inputZip = '/media/sf_So2Sat/data/massive_downloading/0378_index_0033_Adelaide/original_dat/201706/S1A_IW_SLC__1SDV_20170607T200453_20170607T200519_016932_01C2E2_7E63.zip'
    #       template = '/media/sf_So2Sat/sentinel1_data_processing/ma_data_proc_leeflt_2.0/gpt_template_preprocessing_lee.xml'
    #       geoRegion = 'POLYGON ((138.47500610351562 -35.087501525878906, 138.75 -35.087501525878906, 138.75 -34.775001525878906, 138.47500610351562 -34.775001525878906, 138.47500610351562 -35.087501525878906, 138.47500610351562 -35.087501525878906))'
    #       region = '0,0,25234,17679'

    try:
        gptdir = os.environ['gpt']
    except:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:   Directory to ESA SNAP TOOLBOX GPT not found in environment variables")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return 0

    city = inputZip.split('/')[-4]
    time = inputZip.split('/')[-2]
    
    if procFlag == 1:
        outputData = inputZip.replace('original_dat',unfiltStringList[0])
        outputData = outputData.replace('.zip',unfiltStringList[1])
    elif procFlag == 2:
        outputData = inputZip.replace('original_dat',leefilStringList[0])
        outputData = outputData.replace('.zip',leefilStringList[1])
    elif procFlag == 3:
        outputData = inputZip.replace('original_dat','water_mask')
        outputData = outputData.replace('.zip','_water_mask.tif')
    elif procFlag == 4:
        outputData = inputZip.replace('original_dat','rangeAzimuth_dat')
        outputData = outputData.replace('.zip','_Orb_Cal_Deb_Sub.dim')
    elif procFlag == 5:
        outputData = inputZip.replace('original_dat','rangeAzimuth_nlm_dat')
        outputData = outputData.replace('.zip','_Orb_Cal_Deb_Spk_Sub.dim')

    else:
        print("ERROR:  INDICATED PROCESSING (procFlag) IS NOT YET SUPPORTED")
        exit(1)



    outputPath = '/'.join(outputData.split('/')[:-1])
    tree = et.parse(template)
    root = tree.getroot()
    
    for node in root.findall('node'):    
        if node[0].text == 'Read':
            node[2][0].text = inputZip
        elif node[0].text == 'Write':
            node[2][0].text = outputData
        elif node[0].text == 'Subset':
            node[2][1].text = region
            node[2][2].text = geoRegion
        elif node[0].text == 'Terrain-Correction' and projection != 0:
            node[2][9].text = projection

    # XML File configure
    if not os.path.exists(outputPath):
	    os.makedirs(outputPath)
    if procFlag == 1:
        xmldir = outputPath + "/Preprocessing_Orb_Cal_Deb_TC_SUB.xml"
        print("   ")
        print("#############################################################")
        print("INFO:    Data of the city "+city+" at the time of "+time)
        print("INFO:    Apply orbit file, calibration, deburst, terrain correction, subset: ")
    elif procFlag == 2:
        xmldir = outputPath + "/Preprocessing_Orb_Cal_Deb_Spk_TC_SUB.xml"
        print("   ")
        print("#############################################################")
        print("INFO:    Data of the city "+city+" at the time of "+time)
        print("INFO:    Apply orbit file, calibration, deburst, Lee filtering, terrain correction, subset: ")
    elif procFlag == 3:
        xmldir = outputPath + "/_water_mask.xml"
        print("   ")
        print("#############################################################")
        print("INFO:    Water mask for data of the city "+city+" at the time of "+time)
        print("INFO:    Apply orbit file, calibration, deburst, filtering, terrain correction, subset: ")
    elif procFlag == 4:
        xmldir = outputPath + "/Preprocessing_Orb_Cal_Deb_Sub.xml"
        print("   ")
        print("#############################################################")
        print("INFO:    range azimuth data in complex form of the city "+city+" at the time of "+time)
        print("INFO:    Apply orbit file, calibration, deburst, subset: ")
    elif procFlag == 5:
        xmldir = outputPath + "/Preprocessing_Orb_Cal_Deb_Spk_Sub.xml"
        print("   ")
        print("#############################################################")
        print("INFO:    range azimuth data in covariance matrix form of the city "+city+" at the time of "+time)
        print("INFO:    Apply orbit file, calibration, deburst, filtering, subset: ")



    # write the graph xml
    tree.write(xmldir)
    
    if os.path.exists(outputData):
        print('INFO:    Output file exist')
        print("#############################################################")
        print("   ")
        subprocess.call([gptdir,xmldir])
        return 2, outputData
    else:
        subprocess.call([gptdir,xmldir])
        print('INFO:    process done')
        print("#############################################################")
        print("   ")
        return 1, outputData




def getGeoRegion(cpath,kmlCityList):
    # This function read the unique index of city for data indicated by cpath, and then find the coordinates of the corresponding ROI
    # Input
    #       -- cpath        - path to the file of city, where data saved
    #       -- kmlCityList  - path to the ROI kml file 
    #
    # Output
    #       -- geoRegion    - WKT format coordinate of ROI in longitude and latitude
    #       -- centerPoint  - longitude and latitude of the center point to the ROI


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
        
    # convert the text coordinate into WKT coordinate
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

    centerPoint = np.array([np.float32(xmin+xmax)/2,np.float32(ymin+ymax)/2])

    # create a polygon
    ring = ogr.Geometry(ogr.wkbLinearRing)                 
    ring.AddPoint(xmin,ymin)
    ring.AddPoint(xmax,ymin)
    ring.AddPoint(xmax,ymax)
    ring.AddPoint(xmin,ymax)
    ring.AddPoint(xmin,ymin)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    geoRegion = poly.ExportToWkt()
    return geoRegion, centerPoint
  
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

def roiLatlon2UTM(WGSPoint,outputEPSG=0):
    # This function transfers geographical coordinate (lon-lat) into WGS 84 / UTM zone coordinate using GDAL
    # Input:
    #       -- WGSPoint       - A N by M array of lon-lat coordinate; N is number of points, 1st col is longitude, 2nd col is latitude
    #       -- outputEPSG     - targeting UTM zone code
    #
    # Output:
    #       -- UTMPoints      - A N by M array of WGS 84 /UTM zone coordinate; N is number of points, 1st col is X, 2nd col is Y
    #       -- outputEPSG     - A UTM EPSG code calculated from the center of ROI
    #       -- utmProjInfo    - A string contains comprehensive utm projection information
    #

    WGSPoint = np.array(WGSPoint).astype(np.float64)

    if len(WGSPoint.shape)==1:
        WGSPoint = np.stack((WGSPoint,WGSPoint),axis=0)
        nb,dim = np.shape(WGSPoint)
    elif len(WGSPoint.shape)==2:
        # number of WGSPoint
        nb,dim = np.shape(WGSPoint)

    elif len(WGSPoint.shape)==3:
        print('ERROR:   DIMENSION OF POINTS SHOULD NO MORE THAN TWO')

    # geographic coordinate (lat-lon) WGS84
    inputEPSG = 4326
    # WGS 84 / UTM zone
    if outputEPSG==0:
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
        p.AddPoint(WGSPoint[i][1], WGSPoint[i][0])
        p.Transform(coordTransform)
        UTMPoints[i][0] = p.GetX()
        UTMPoints[i][1] = p.GetY()


    return UTMPoints, outputEPSG, utmProjInfo
   
   
def latlon2utm(points):
    # This function transfers geographical coordinate (lon-lat) into WGS 84 / UTM zone coordinate using GDAL
    # Input:
    #       -- points       - A N by M array of lon-lat coordinate; N is number of points, 1st col is longitude, 2nd col is latitude
    #
    # Output: 
    #       -- points       - A N by M array of WGS 84 /UTM zone coordinate; N is number of points, 1st col is X, 2nd col is Y
    #

    points = np.array(points)

    if len(points.shape)==1:
        points = np.stack((points,points),axis=0)
        nb,dim = np.shape(points)
    elif len(points.shape)==2:
        # number of points
        nb,dim = np.shape(points)

    elif len(points.shape)==3:
        print('ERROR:   DIMENSION OF POINTS SHOULD NO MORE THAN TWO')
 
    # geographic coordinate (lat-lon) WGS84
    inputEPSG = 4326
    # WGS 84 / UTM zone
    if points[0][1]<0:
        outputEPSG = 32700
    else:
        outputEPSG = 32600
    
    outputEPSG = int(outputEPSG + np.floor((points[0][0]+180)/6) + 1)
    
#    # WGS 84 / Pseudo-Mercator
#    outputEPSG = 3857    
    
    # create coordinate transformation
    inSpatialRef = osr.SpatialReference()
    inSpatialRef.ImportFromEPSG(inputEPSG)
    
    outSpatialRef = osr.SpatialReference()
    outSpatialRef.ImportFromEPSG(outputEPSG)
    
    utmProjInfo = outSpatialRef.ExportToWkt()

    coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)
    
    # transform point        
    
    for i in range(0,np.size(points,axis=0)):
        p = ogr.Geometry(ogr.wkbPoint)
        p.AddPoint(points[i][0], points[i][1])
        p.Transform(coordTransform)
        points[i][0] = p.GetX()
        points[i][1] = p.GetY()
    
    return points,utmProjInfo
    
    
    
def getRegion(cpath,kmlCityList):
    # setting the resolution of raster image
    res = 10
    # read the unique index of city
    temp = cpath.split('/')[-1].split('_') 
    idx = int(temp[1])
    
    # find the ROI coordinate of the city    
    tree = et.parse(kmlCityList)
    for item in tree.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        if item[1][0][3].text == str(idx):
            found = item
            break
        
    # convert the text coordinate into WKT coordinate
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
    points = np.array([[xmin,ymin],[xmax,ymax]])
    
    # convert geographic coordinate into WGS 84 / UTM zone coordinate
    points,_ = latlon2utm(points)
    widHei = np.round((points[1]-points[0])/res)
    widHei = widHei.astype(int)
    region = '0,0,'+str(widHei[0])+','+str(widHei[1])
    return region
    
    
    
    
    
def getPathOfCity(dpath):
    # dpath = '/media/sf_So2Sat/data/massive_downloading'
    cityPath = glob.glob(dpath+'/*')
    i = 0
    while i < len(cityPath):        
        cpath = cityPath[i]
        temp = cityPath[i].split('/')[-1].split('_')
        i = i + 1
        if not os.path.isdir(cpath) or len(temp)!=3:
            print(cpath)
            print('The directory is either not a directory, or is not named in standard. And it has been removed')
            cityPath.remove(cpath)
            i = i - 1            
    return cityPath
    

def getPathOfTime(cpath):
    timePath = glob.glob(cpath+'/original_dat/*')
    return timePath
    
    
def getPath2Data(tpath):
    zipPath = glob.glob(tpath+'/*.zip')
    return zipPath



def gdalMosaic(zipPath, procFlag, utmEPSG, extent=0, resolution = 10):
    extent = np.array(extent)
    # mosaic data of unfiltered, lee filtered, and water mask
    if procFlag == 1:
        inputPath  = zipPath[0].replace('original_dat','geocoded_subset_unfilt_dat')
        outputPath = zipPath[0].replace('original_dat','mosaic_unfilt_dat')
    elif procFlag == 2:
        inputPath  = zipPath[0].replace('original_dat','geocoded_subset_dat')
        outputPath = zipPath[0].replace('original_dat','mosaic_dat')
    elif procFlag == 3:
        inputPath  = zipPath[0].replace('original_dat','water_mask')
        outputPath = zipPath[0].replace('original_dat','mosaic_water_mask')
    elif procFlag == 4:
        inputPath  = zipPath[0].replace('original_dat','geocoded_unfilt_Hres_dat')
        outputPath = zipPath[0].replace('original_dat','mosaic_unfilt_Hres_dat')
    elif procFlag == 5:
        inputPath  = zipPath[0].replace('original_dat','geocoded_Hres_dat')
        outputPath = zipPath[0].replace('original_dat','mosaic_nlm_Hres_dat')





    inputPath = '/'.join(inputPath.split('/')[:-1])+'/*.tif'
    files = glob.glob(inputPath)
    image_name = '/'.join(files[0].split('/')[-3:]) 

    outputPath = '/'.join(outputPath.split('/')[:-1])
    mosaicpath = outputPath +'/mosaic.tif'

    if os.path.exists(mosaicpath):   
        subprocess.call(['rm',mosaicpath])


    if len(zipPath)==1:
        # only one data covers ROI, no mosaic needed
        # but make symbolic link
        
        # make directory if not exist
        if not os.path.exists(outputPath):
            os.makedirs(outputPath)
        
        # >>Jingliang, please comment
        if extent.shape[0] == 1:
            subprocess.call(['ln', '-s', '../../'+image_name, mosaicpath])
            return 3
        elif extent.shape[0] == 4:
            comm = ['gdalwarp','-multi','-wo','NUM_THREADS=4','-t_srs','EPSG:'+str(utmEPSG),'-srcnodata', '0', '-dstnodata', '0', '-tr', str(resolution), str(resolution), '-te', str(extent[0]), str(extent[2]), str(extent[1]), str(extent[3]) ]
            for idxfile in range(0,len(files)):
                comm.append(files[idxfile])
            comm.append(mosaicpath)
            subprocess.call(comm)
            return comm


    elif len(zipPath)>1:
        # more than one data cover ROI, mosaicing needed
        # forming the gdalwarp command

        # >>Jingliang, pleaser comment
        if extent.shape[0] == 1:
            comm = ['gdalwarp','-multi','-wo','NUM_THREADS=4','-srcnodata', '0', '-dstnodata', '0']
            for idxfile in range(0,len(files)):
                comm.append(files[idxfile])
            comm.append(mosaicpath)
        elif extent.shape[0] == 4:
            comm = ['gdalwarp','-multi','-wo','NUM_THREADS=4','-t_srs','EPSG:'+str(utmEPSG), '-srcnodata', '0', '-dstnodata', '0', '-tr', str(resolution), str(resolution), '-te', str(extent[0]), str(extent[2]), str(extent[1]), str(extent[3]) ]
            for idxfile in range(0,len(files)):
                comm.append(files[idxfile])
            comm.append(mosaicpath)
        else: 
            print('ERROR:    THE GIVEN EXTENT IN MOSAICING IS WRONG ')
            print("   ")


        # overwrite existed mosaiced file
        if os.path.exists(mosaicpath):
            # mosaiced data already exists
            print('INFO:    Output file exist, now overwriting ')
            print("   ")
            subprocess.call(comm)
            return 2
        elif not os.path.exists(outputPath):
            os.makedirs(outputPath)
            subprocess.call(comm)
            return comm
        else :
            # the directory exists, but mosaic file does not exist
            subprocess.call(comm)
            return comm


def getProjTiff(cpath,tiffFolder):
# get WGS84/UTM projection from geotiff
    dataCityName = cpath.split('/')[-1].split('_')
    dataCityName = dataCityName[-1].lower()
    tiffCities = glob.glob(tiffFolder+'/*')
    for i in range(0,len(tiffCities)):
        tiffcity = tiffCities[i].split('/')[-1]
        cityName = tiffcity.replace('_','')
#        print cityName,tiffcity
        if cityName in dataCityName:
            tiffPath = tiffCities[i]+'/'+tiffcity+'_lcz_GT.tif'
            try:
                tifdat = gdal.Open(tiffPath)
            except Exception:
                tiffPath.replace('.tif','.TIF')
                tifdat = gdal.Open(tiffPath)
            break
    # map projection
    proj = tifdat.GetProjectionRef()

    return proj


def getTiffExtent(cpath,tiffFolder):
# get the geographic extent of tiff file
    dataCityName = cpath.split('/')[-1].split('_')
    dataCityName = dataCityName[-1].lower()
    tiffCities = glob.glob(tiffFolder+'/*')
    for i in range(0,len(tiffCities)):
        tiffcity = tiffCities[i].split('/')[-1]
        cityName = tiffcity.replace('_','')
        if cityName in dataCityName:
            tiffPath = tiffCities[i]+'/'+tiffcity+'_lcz_GT.tif'
            try:
                tifdat = gdal.Open(tiffPath)
                # xmin, xres, xskew, ymax, yskew, yres  = tifdat.GetGeoTransform()
            except Exception:
                tiffPath.replace('.tif','.TIF')
                tifdat = gdal.Open(tiffPath)
                # xmin, xres, xskew, ymax, yskew, yres  = tifdat.GetGeoTransform()
            xmin, xres, xskew, ymax, yskew, yres  = tifdat.GetGeoTransform()
            proj = osr.SpatialReference(wkt=tifdat.GetProjection())
            utmEPSG = np.int(proj.GetAttrValue('AUTHORITY',1))
            break

    xmax = xmin + (tifdat.RasterXSize * xres)
    ymin = ymax + (tifdat.RasterYSize * yres)

    return xmin,xmax,ymin,ymax,utmEPSG

 
def getGeoRegionTiff(cpath,tiffFolder):
    dataCityName = cpath.split('/')[-1].split('_') 
    dataCityName = dataCityName[-1].lower()
    tiffCities = glob.glob(tiffFolder+'/*')
    for i in range(0,len(tiffCities)):
        tiffcity = tiffCities[i].split('/')[-1]
        cityName = tiffcity.replace('_','')
        if cityName in dataCityName:
            tiffPath = tiffCities[i]+'/'+tiffcity+'_lcz_GT.tif'
            try:
                tifdat = gdal.Open(tiffPath)
                ulx, xres, xskew, uly, yskew, yres  = tifdat.GetGeoTransform()
            except Exception:
                tiffPath.replace('.tif','.TIF')
                tifdat = gdal.Open(tiffPath)
                ulx, xres, xskew, uly, yskew, yres  = tifdat.GetGeoTransform()                
            break
    lrx = ulx + (tifdat.RasterXSize * xres)
    lry = uly + (tifdat.RasterYSize * yres)    

    # buffering
    x_buffer = 1000
    y_buffer = 1000

    ulx = ulx - x_buffer
    lrx = lrx + x_buffer
    lry = lry - y_buffer
    uly = uly + y_buffer



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

    # map projection
    xmin = coordinate[0]
    xmax = coordinate[1]
    ymin = coordinate[2]
    ymax = coordinate[3]


    ring = ogr.Geometry(ogr.wkbLinearRing)
    ring.AddPoint(xmin,ymin)
    ring.AddPoint(xmax,ymin)
    ring.AddPoint(xmax,ymax)
    ring.AddPoint(xmin,ymax)
    ring.AddPoint(xmin,ymin)
    poly = ogr.Geometry(ogr.wkbPolygon)
    poly.AddGeometry(ring)
    georegion = poly.ExportToWkt()

    return georegion
    

        
def getRegionTiff(cpath,tiffFolder):
    dataCityName = cpath.split('/')[-1].split('_') 
    dataCityName = dataCityName[-1].lower()
    tiffCities = glob.glob(tiffFolder+'/*')

    for i in range(0,len(tiffCities)):
        tiffcity = tiffCities[i].split('/')[-1]
        cityName = tiffcity.replace('_','')
#        print cityName,tiffcity
        if cityName in dataCityName:
            tiffPath = tiffCities[i]+'/'+tiffcity+'_lcz_GT.tif'
            try:
                tifdat = gdal.Open(tiffPath)
                ulx, xres, xskew, uly, yskew, yres  = tifdat.GetGeoTransform()
            except Exception:
                tiffPath.replace('.tif','.TIF')
                tifdat = gdal.Open(tiffPath)
                ulx, xres, xskew, uly, yskew, yres  = tifdat.GetGeoTransform()                
            break
        
    lrx = ulx + (tifdat.RasterXSize * xres)
    lry = uly + (tifdat.RasterYSize * yres)    
                
    width = int((lrx-ulx)/10+100)
    height = int((uly-lry)/10+100)
    region = '0,0,'+str(width)+','+str(height)
    return region


def readSEN1TIFF2NLSAR(path):
# this function read Sentinel-1 geotiff data, and organizes it into the format of NLSAR software
# path = '/datastore/DATA/classification/SEN1/LCZ42_SEN1/LCZ42_22606_Zurich/rangeAzimuth_dat/201706/S1B_IW_SLC__1SDV_20170602T053407_20170602T053434_005867_00A499_A351_rangeAzimuth.tif'
    try:
        tifID = gdal.Open(path)
    except RuntimeError:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given SENTINEL-1 geotiff can not be open by GDAL")
        print("DIRECTORY:       "+path)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    data = tifID.ReadAsArray()

    dn,rw,cl = data.shape
    nlsardata = np.zeros((rw,cl,2,2),dtype=np.complex64)

    nlsardata[:,:,0,0] = np.square(data[0,:,:])+np.square(data[1,:,:])
    nlsardata[:,:,0,1] = (data[0,:,:]*data[2,:,:]+data[1,:,:]*data[3,:,:])+(data[1,:,:]*data[2,:,:]-data[0,:,:]*data[3,:,:])*1j
    nlsardata[:,:,1,0] = np.conjugate(nlsardata[:,:,0,1])
    nlsardata[:,:,1,1] = np.square(data[2,:,:])+np.square(data[3,:,:])

    return nlsardata

def readSEN1DimComplex2NLSAR(path):
# this function read Sentinel-1 data in its DIM form, and organizes it into the format of NLSAR software
# path = '/datastore/DATA/classification/SEN1/LCZ42_SEN1/LCZ42_22606_Zurich/rangeAzimuth_dat/201706/S1B_IW_SLC__1SDV_20170602T053407_20170602T053434_005867_00A499_A351_Orb_Cal_Deb_Sub.data'
    files = ['/i_VH.img','/q_VH.img','/i_VV.img','/q_VV.img']

    # intial data array to store data in memory
    fid = gdal.Open(path+files[0])
    data = np.zeros((len(files),fid.RasterYSize,fid.RasterXSize),dtype = np.float32)
    del fid

    # read data
    for i in range(0,len(files)):
        fid = gdal.Open(path+files[i])
        data[i,:,:] = fid.ReadAsArray()
        del fid

    # save the data into nlsartoolbox format
    dn,rw,cl = data.shape
    nlsardata = np.zeros((rw,cl,2,2),dtype=np.complex64)

    nlsardata[:,:,0,0] = np.square(data[0,:,:])+np.square(data[1,:,:])
    nlsardata[:,:,0,1] = (data[0,:,:]*data[2,:,:]+data[1,:,:]*data[3,:,:])+(data[1,:,:]*data[2,:,:]-data[0,:,:]*data[3,:,:])*1j
    nlsardata[:,:,1,0] = np.conjugate(nlsardata[:,:,0,1])
    nlsardata[:,:,1,1] = np.square(data[2,:,:])+np.square(data[3,:,:])

    return nlsardata

def nlsarData2SEN1DimCovariance(nlsarData,path):
# this function write NLSAR data covariance matrix into a SEN1 DIM file, in its covariance matrix format
# path = '/datastore/DATA/classification/SEN1/LCZ42_SEN1/LCZ42_22606_Zurich/rangeAzimuth_nlm_dat/201706/S1B_IW_SLC__1SDV_20170602T053407_20170602T053434_005867_00A499_A351_Orb_Cal_Deb_Spk_Sub.data'
    files = ['/C11.img','/C12_real.img','/C12_imag.img','/C22.img']
    from osgeo.gdalconst import GA_Update

    for i in range(0,len(files)):
        fid = gdal.Open(path+files[i],GA_Update)
        saveDat = fid.ReadAsArray()
        bnd = fid.GetRasterBand(1)
        if i == 0:
            saveDat = np.real(nlsarData[:,:,0,0])
        elif i == 1:
            saveDat = np.real(nlsarData[:,:,0,1])
        elif i == 2:
            saveDat = np.imag(nlsarData[:,:,0,1])
        elif i == 3:
            saveDat = np.real(nlsarData[:,:,1,1])
        bnd.WriteArray(saveDat)
        bnd.FlushCache()
        del bnd,fid

def terrainCorrection(dimPath, template, projection):
# this function accomplishes terrain correction using SNAP tool box, mainly for unfiltered data in higher resolution
    try:
        gptdir = os.environ['gpt']
    except:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:   Directory to ESA SNAP TOOLBOX GPT not found in environment variables")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return 0

    # get the directory to the output file
    outputData = dimPath.replace('_Sub.dim','_Sub_TC.tif')
    outputData = outputData.replace('rangeAzimuth_dat','geocoded_unfilt_Hres_dat')
    outputPath = '/'.join(outputData.split('/')[:-1])
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)


    # read and configure XML file
    tree = et.parse(template)
    root = tree.getroot()

    for node in root.findall('node'):
        if node[0].text == 'Read':
            node[2][0].text = dimPath
        elif node[0].text == 'Write':
            node[2][0].text = outputData
        elif node[0].text == 'Terrain-Correction' and projection != 0:
            node[2][9].text = projection

    # save the configuration
    xmldir = outputPath + "/Preprocessing_TC.xml"
    tree.write(xmldir)

    # read and configure XML file
    tree = et.parse(template)
    root = tree.getroot()

    for node in root.findall('node'):
        if node[0].text == 'Read':
            node[2][0].text = dimPath
        elif node[0].text == 'Write':
            node[2][0].text = outputData
        elif node[0].text == 'Terrain-Correction' and projection != 0:
            node[2][9].text = projection

    # save the configuration
    xmldir = outputPath + "/Preprocessing_TC.xml"
    tree.write(xmldir)


    print("#############################################################")
    print("INFO:    Terrain correction of the unfiltered data")
    print("#############################################################")

    subprocess.call([gptdir,xmldir])




def nlmTerrainCorrection(dimPath, template, projection):
# this function accomplishes terrain correction using SNAP tool box, mainly for nlm filtered data in higher resolution
    try:
        gptdir = os.environ['gpt']
    except:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:   Directory to ESA SNAP TOOLBOX GPT not found in environment variables")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return 0

    # get the directory to the output file
    outputData = dimPath.replace('_Sub.dim','_Sub_TC.tif')
    outputData = outputData.replace('rangeAzimuth_nlm_dat','geocoded_Hres_dat')
    outputPath = '/'.join(outputData.split('/')[:-1])
    if not os.path.exists(outputPath):
        os.makedirs(outputPath)


    # read and configure XML file
    tree = et.parse(template)
    root = tree.getroot()

    for node in root.findall('node'):
        if node[0].text == 'Read':
            node[2][0].text = dimPath
        elif node[0].text == 'Write':
            node[2][0].text = outputData
        elif node[0].text == 'Terrain-Correction' and projection != 0:
            node[2][9].text = projection

    # save the configuration
    xmldir = outputPath + "/Preprocessing_TC.xml"
    tree.write(xmldir)

    
    print("#############################################################")
    print("INFO:    Terrain correction of the nlm filtered data")
    print("#############################################################")

    subprocess.call([gptdir,xmldir])















