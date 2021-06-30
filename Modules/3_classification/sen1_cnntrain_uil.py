# -*- coding: utf-8 -*-
"""
Created on Tue May 22 15:09:53 2018

@author: hu jingliang
"""

'modified by jingliang, 07.09.2018 11:52 a.m. added feature extraction of real and imaginary part of unfiltered data'

# Last modified: 09.07.2018 14:41:00 Jingliang Hu
# handling the situation that data does not cover all label, changed funcion 'getCoordinate'





import os
import glob
import numpy as np
from osgeo import gdal
import sys
import h5py
gdal.UseExceptions()
#from __future__ import print_function

def cityListFromFolder(cityListFolder):
    # cityListFolder = '/media/sf_So2Sat/auxdata/citylists/citylistLCZ9'
    # cityListFolder = '/media/sf_So2Sat/auxdata/citylists/citylistOne'
    cityList = glob.glob(cityListFolder+'/*')
    if type(cityList) is list:
        for i in range(0,len(cityList)):
            cityList[i] = cityList[i].split('/')[-1]
    elif type(cityList) is str:
        cityList = cityList.split('/')[-1]
    else:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       reading city list failed")
        print("DIRECTORY:   " + cityListFolder)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    return cityList

def getPathOfCity(dpath):
    # dpath = '/media/sf_So2Sat/data/massive_downloading'
    cityPath = glob.glob(dpath+'/*')
    i = 0
    while i < len(cityPath):
        cpath = cityPath[i]
        temp = cityPath[i].split('/')[-1].split('_')
        i = i + 1
        if not os.path.isdir(cpath) or len(temp)!=3:
            #print cpath
            print ('The directory is either not a directory, or is not named in standard. And it has been removed')
            cityPath.remove(cpath)
            i = i - 1
    return cityPath

def dataOfCityList(cityList,dataStorePath):
    # dataStorePath = '/media/sf_So2Sat/data'
    dataOfCity = getPathOfCity(dataStorePath)
    unfiltMosaicDataOfCity = []
    if type(cityList) is list:
        for i in range(0,len(cityList)):
            for j in range(0,len(dataOfCity)):
                if cityList[i].replace('_','') in dataOfCity[j].split('/')[-1].lower():
                    temp = glob.glob(dataOfCity[j]+'/mosaic_unfilt_dat/*/mosaic.tif')
                    for name in temp:
                        unfiltMosaicDataOfCity.append(name)
                    break
                elif j == len(dataOfCity)-1:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    print("WARNING:")
                    print('Data for city of '+cityList[i]+' not found')
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    elif type(cityList) is str:
        for j in range(0,len(dataOfCity)):
            if cityList.replace('_','') in dataOfCity[j].split('/')[-1].lower():
                temp = glob.glob(dataOfCity[j]+'/mosaic_unfilt_dat/*/mosaic.tif')
                for name in temp:
                    unfiltMosaicDataOfCity.append(name)
                break
            elif j == len(dataOfCity)-1:
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print("WARNING:")
                print('Data for city of '+cityList+' not found')
                print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       error in given city list")
        print("DIRECTORY:   " + cityList)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    return unfiltMosaicDataOfCity




def getPathOfTime(cpath):
    tempPath = cpath+'/mosaic_unfilt_dat'
    city = cpath.split('/')[-1]

    if not os.path.exists(tempPath):
        tempPath = tempPath.replace('mosaic_unfilt_dat','geocoded_subset_unfilt_dat')

    timePath = glob.glob(tempPath + '/*')
    if len(timePath)==0:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       can not find preprocessed unfiltered data for the city of: " + city)
        print("DIRECTORY:   " + tempPath)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    return timePath


def getPath2Data(tpath):
    tifPath = glob.glob(tpath+'/*.tif')
    if len(tifPath)==0:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       can not find data ")
        print("DIRECTORY:   " + tpath)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    if len(tifPath) > 1:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       more than one data found for a city at a time period ")
        print("DIRECTORY:   " + tifPath)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    return tifPath[0]


def getImagCoord(dir2DataGeotiff,xWorld,yWorld):
# find the number of rows and columns with given geographic coordinate. Given coordinate should be in WGS 84/UTM
    try:
        dataTif = gdal.Open(dir2DataGeotiff)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given data geotiff can not be open by GDAL")
        print("DIRECTORY:       "+dir2DataGeotiff)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)


    geoInfoData = dataTif.GetGeoTransform()

    col_dat = np.round((xWorld - geoInfoData[0])/geoInfoData[1])
    row_dat = np.round((geoInfoData[3] - yWorld)/np.abs(geoInfoData[5]))

    return col_dat,row_dat


def getCoordinate(gtPath,dataPath):
    # find the data corresponds to label location, based on the geo-coordinate
    try:
        labelTif = gdal.Open(gtPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given ground truth geotiff can not be open by GDAL")
        print("DIRECTORY:       "+gtPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)


    try:
        dataTif = gdal.Open(dataPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given data geotiff can not be open by GDAL")
        print("DIRECTORY:       "+dataPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)


    # read label data and find data corresponds to label location
    label = labelTif.ReadAsArray()
    label[label<0] = 0
    label[label>100] = label[label>100]-90

    row_lab,col_lab = np.where(label>0)
    geoInfoLabel = labelTif.GetGeoTransform()
    geoInfoData = dataTif.GetGeoTransform()


    xWorld = geoInfoLabel[0] + col_lab * geoInfoLabel[1];
    yWorld = geoInfoLabel[3] + row_lab * geoInfoLabel[5];

    col_dat = np.round((xWorld - geoInfoData[0])/geoInfoData[1])
    row_dat = np.round((geoInfoData[3] - yWorld)/np.abs(geoInfoData[5]))



    outDataBoundary = np.where(col_dat<0)
    if outDataBoundary[0].size>0:
        print('West part of ground truth is not covered by data')
        row_dat = np.delete(row_dat,outDataBoundary,0)
        col_dat = np.delete(col_dat,outDataBoundary,0)
        row_lab = np.delete(row_lab,outDataBoundary,0)
        col_lab = np.delete(col_lab,outDataBoundary,0)
        xWorld  = np.delete(xWorld,outDataBoundary,0)
        yWorld  = np.delete(yWorld,outDataBoundary,0)

    outDataBoundary = np.where(row_dat<0)
    if outDataBoundary[0].size>0:
        print('North part of ground truth is not covered by data')
        row_dat = np.delete(row_dat,outDataBoundary,0)
        col_dat = np.delete(col_dat,outDataBoundary,0)
        row_lab = np.delete(row_lab,outDataBoundary,0)
        col_lab = np.delete(col_lab,outDataBoundary,0)
        xWorld  = np.delete(xWorld,outDataBoundary,0)
        yWorld  = np.delete(yWorld,outDataBoundary,0)

    outDataBoundary = np.where(row_dat>dataTif.RasterYSize)
    if outDataBoundary[0].size>0:
        print('South part of ground truth is not covered by data')
        row_dat = np.delete(row_dat,outDataBoundary,0)
        col_dat = np.delete(col_dat,outDataBoundary,0)
        row_lab = np.delete(row_lab,outDataBoundary,0)
        col_lab = np.delete(col_lab,outDataBoundary,0)
        xWorld  = np.delete(xWorld,outDataBoundary,0)
        yWorld  = np.delete(yWorld,outDataBoundary,0)

    outDataBoundary = np.where(col_dat>dataTif.RasterXSize)
    if outDataBoundary[0].size>0:
        print('East part of ground truth is not covered by data')
        row_dat = np.delete(row_dat,outDataBoundary,0)
        col_dat = np.delete(col_dat,outDataBoundary,0)
        row_lab = np.delete(row_lab,outDataBoundary,0)
        col_lab = np.delete(col_lab,outDataBoundary,0)
        xWorld  = np.delete(xWorld,outDataBoundary,0)
        yWorld  = np.delete(yWorld,outDataBoundary,0)

    return col_dat,row_dat,xWorld,yWorld,row_lab,col_lab



def boxcar(data,halfwin):
    shiftInter = np.linspace(-halfwin,halfwin,num=2*halfwin+1)
    res = np.zeros(data.shape)
    for i in shiftInter:
        for j in shiftInter:
            res = res + np.roll(np.roll(data,int(j),axis=2),int(i),axis=1)
    res = res/np.square((2*halfwin+1))
    return res

def dBFeatStat(data,datamask):
    temp = data[datamask]
    if np.sum(temp==0)>0:
        print('FOUND INTENSITY EQUALLS ZEROS AND SET TO EPS')
        print('number of zeros: '+ str(np.sum(temp==0)))
        temp[temp==0] = np.finfo(temp.dtype).eps
    temp = 10*np.log10(temp)
    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.finfo(data.dtype).min

    stat = {}
    stat['min'] = np.min(temp[temp>10*np.log10(np.finfo(temp.dtype).eps)])
    stat['max'] = np.max(temp)
    bins = np.arange(-60, 52, 3)

    #print(np.max(temp))
    #print(np.min(temp))


    freq,_ = np.histogram(temp,bins)
    stat['freq'] = freq
    stat['bins'] = bins
    stat['mean'] = np.mean(temp)
    stat['std'] = np.std(temp)
    return dataRes, stat



def dBFeatNorm(data,datamask,flag=2):
    temp = data[datamask]
    temp = 10*np.log10(temp)
    if flag==1:
        valRange = np.max(temp[:])-np.min(temp[:])
        temp = (temp - np.min(temp[:]))/valRange
    elif flag==2:
        # stretching data after clipping the left and right tails of the pdf by 2%
        # Gamba, Paolo, Massimilano Aldrighi, and Mattia Stasolla. "Robust extraction of urban area extents in HR and VHR SAR images." IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing 4.1 (2011): 27-34.
        maxV = np.max(temp)
        minV = np.min(temp)
        #clip = (maxV-minV)*0.02
        #temp[temp<(minV+clip)] = (minV+clip)
        #temp[temp>(maxV-clip)] = (maxV-clip)
        temp = (temp-(minV))/(maxV-minV)

    elif flag==3:
        maxV = np.max(temp)
        minV = np.min(temp)
        clip = (maxV-minV)*0.04
        strSca = maxV - clip
        alignPnt = np.median(temp[temp>strSca])
        temp = temp + (100 - alignPnt)
    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.min(temp[:])
    return dataRes

def dBFeatNorm_Gamba(data):
    # stretching data after clipping the left and right tails of the pdf by 2%
    # Gamba, Paolo, Massimilano Aldrighi, and Mattia Stasolla. "Robust extraction of urban area extents in HR and VHR SAR images." IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing 4.1 (2011): 27-34.
    datamask = data!=0
    temp = data[datamask]
    temp = 10*np.log10(temp)
    maxV = np.max(temp)
    minV = np.min(temp)
    clip = (maxV-minV)*0.02
    temp[temp<(minV+clip)] = (minV+clip)
    temp[temp>(maxV-clip)] = (maxV-clip)

    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.min(temp[:])
    return dataRes

def dBFeatNorm_strongScatter(data):
    datamask = data!=0
    temp = data[datamask]
    temp = 10*np.log10(temp)
    strSca = np.percentile(temp,96)
    alignPnt = np.median(temp[temp>strSca])
    temp = temp + (100 - alignPnt)

    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.min(temp[:])
    return dataRes

def realImagFeatStat(data,datamask):
    temp = data[datamask]
    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.finfo(data.dtype).min

    stat = {}
    rangeTemp = temp
    bins = np.arange(np.min(rangeTemp), np.max(rangeTemp), np.ptp(rangeTemp)/100)
    freq,_ = np.histogram(rangeTemp,bins)
    stat['freq'] = freq
    stat['bins'] = bins
    stat['mean'] = np.mean(rangeTemp)
    stat['std'] = np.std(rangeTemp)
    return dataRes, stat



def featStat(data,datamask):
    temp = data[datamask]
    if np.sum(temp==0)>0:
        print('FOUND INTENSITY EQUALLS ZEROS AND SET TO EPS')
        print('number of zeros: '+ str(np.sum(temp==0)))
        temp[temp==0] = np.finfo(temp.dtype).eps
    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.finfo(data.dtype).min

    stat = {}
    rangeTemp = temp[temp!=np.finfo(temp.dtype).eps]
    rangeTemp = rangeTemp[np.isnan(rangeTemp)==False]
    bins = np.arange(np.min(rangeTemp), np.max(rangeTemp), np.ptp(rangeTemp)/100)
    freq,_ = np.histogram(rangeTemp,bins)
    stat['freq'] = freq
    stat['bins'] = bins
    stat['mean'] = np.mean(rangeTemp)
    stat['std'] = np.std(rangeTemp)
    return dataRes, stat

def featNorm(data,datamask):
    temp = data[datamask]
    valRange = np.max(temp[:])-np.min(temp[:])
    temp = (temp - np.min(temp[:]))/valRange

    dataRes = np.zeros(data.shape)
    dataRes[datamask] = temp
    dataRes[datamask==False] = np.min(temp[:])
    return dataRes


def getData(dataPath, featSelection = [0,0,0,0,0,0,0,0,0,0,0]):


    # featSelection: a 1 by 11 vector indicating which features should be extract.
    #
    # e.g. [1,1,0,1,1,1,0] means extract 5 features: VH_dB_un, VV_dB_un, VH_dB_un, VV_dB_un and COH_lee
    # by now, feature selection only support in total 7 features,
    # ------------------------------------------------------------------------------------
    #           Feature                 |    Shortcuts  |  delete code  |  preserving code
    # ------------------------------------------------------------------------------------
    #       unfiltered VH in dB         |    VH_dB_un   |      0        |        1
    #       unfiltered VV in dB         |    VV_dB_un   |      0        |        1
    #       boxcar coherence            |    COH_boxcar |      0        |        1
    #       VH real part                |    VH_real    |      0        |        1
    #       VH imag part                |    VH_imag    |      0        |        1
    #       VV real part                |    VV_real    |      0        |        1
    #       VV imag part                |    VV_imag    |      0        |        1
    #       lee-filtered VH in dB       |    VH_dB_lee  |      0        |        1
    #       lee-filtered VV in dB       |    VV_dB_lee  |      0        |        1
    #       lee-filtered coherence      |    COH_lee    |      0        |        1
    #       lee-filtered relative phase |    PHA_lee    |      0        |        1
    # -------------------------------------------------------------------------------------
    #
    #
    # dataPath = '/data/hu/LCZ42_SEN1/LCZ42_23052_LosAngeles-LongBeach-SantaAna/mosaic_unfilt_dat/201706/mosaic.tif'
    # featSelection = [1,1,0,1,1,1,0]
    # if featSelection = [0,0,0,0,0,0,0] return data mask and unfiltered data


    # generate data mask from lee-filtered data
    maskPath = dataPath.replace('unfilt_','')
    try:
        print(maskPath)
        maskTif = gdal.Open(maskPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given data geotiff can not be open by GDAL")
        print("DIRECTORY:       "+dataPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    data = maskTif.ReadAsArray()
    # data mask extraction
    datamask = (data[0,:,:]+data[3,:,:])>0
    del(maskTif)
    del(data)


    # initial a dictionary to save maximum, minimum, histogram of intensity bands
    stat = {}

    # unfiltered data need to be loaded
    if np.sum(featSelection[:7]) > 0:
        try:
            dataTif = gdal.Open(dataPath)
        except RuntimeError as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("ERROR:           the given data geotiff can not be open by GDAL")
            print("DIRECTORY:       "+dataPath)
            print("GDAL EXCEPCTION: "+e)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sys.exit(1)
        # read data
        data = dataTif.ReadAsArray()
        data[np.isnan(data)] = 0
        VH_real = data[0,:,:].copy()
        VH_imag = data[1,:,:].copy()
        VV_real = data[2,:,:].copy()
        VV_imag = data[3,:,:].copy()

        # convert complex form into covariance matrix form
        tempData = np.zeros(data.shape)
        tempData[0,:,:] = data[0,:,:]*data[0,:,:] + data[1,:,:]*data[1,:,:]
        tempData[1,:,:] = data[2,:,:]*data[2,:,:] + data[3,:,:]*data[3,:,:]
        tempData[2,:,:] = data[0,:,:]*data[2,:,:] + data[1,:,:]*data[3,:,:]
        tempData[3,:,:] = data[1,:,:]*data[2,:,:] - data[0,:,:]*data[3,:,:]
        data = tempData
        del(tempData)

        # get intensity of VV, VH; get boxcar coherence
        VH_dB_un = data[0,:,:]
        VV_dB_un = data[1,:,:]
        data = boxcar(data,1)
        VH_dB_un[VH_dB_un==0] = data[0,VH_dB_un==0]
        VV_dB_un[VV_dB_un==0] = data[1,VV_dB_un==0]
        COH_boxcar = np.sqrt(np.add(np.square(data[2,:,:]),np.square(data[3,:,:])))/np.sqrt(data[1,:,:]*data[0,:,:])
        del(data)

        # convert intensity into dB, and normalization
        if featSelection[0]==1:
            #print(' unfiltered VH:')
            VH_dB_un, stat['VHdB'] = dBFeatStat(VH_dB_un,datamask)
        else:
            del(VH_dB_un)

        if featSelection[1]==1:
            #print(' unfiltered VV:')
            VV_dB_un, stat['VVdB'] = dBFeatStat(VV_dB_un,datamask)
        else:
            del(VV_dB_un)

        if featSelection[2]==1:
            #print(' boxcar coherence:')
            COH_boxcar, stat['coh'] = featStat(COH_boxcar,datamask)
        else:
            del(COH_boxcar)

        if featSelection[3]==1:
            #print(' VH real part:')
            VH_real, stat['VH_real'] = realImagFeatStat(VH_real,datamask)
        else:
            del(VH_real)
        if featSelection[4]==1:
            #print(' VH imaginary part:')
            VH_imag, stat['VH_imag'] = realImagFeatStat(VH_imag,datamask)
        else:
            del(VH_imag)
        if featSelection[5]==1:
            #print(' VV real part:')
            VV_real, stat['VV_real'] = realImagFeatStat(VV_real,datamask)
        else:
            del(VV_real)
        if featSelection[6]==1:
            #print(' VV imaginary part:')
            VV_imag, stat['VV_imag'] = realImagFeatStat(VV_imag,datamask)
        else:
            del(VV_imag)


        del(dataTif)

    if np.sum(featSelection[7:]) > 0:
        # lee-filtered data need to be loaded
        dataPath = dataPath.replace('unfilt_','')
        try:
            dataTif = gdal.Open(dataPath)
        except RuntimeError as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("ERROR:           the given data geotiff can not be open by GDAL")
            print("DIRECTORY:       "+dataPath)
            print("GDAL EXCEPCTION: "+e)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sys.exit(1)

        data = dataTif.ReadAsArray()

        data = np.stack((data[0,:,:],data[3,:,:],data[1,:,:],data[2,:,:]))

        if featSelection[7]==1:
            #print(' LEE filtered VH:')
            VH_dB_lee, stat['VH_dB_lee'] = dBFeatStat(data[0,:,:],datamask)
        if featSelection[8]==1:
            #print(' LEE filtered VV:')
            VV_dB_lee, stat['VV_dB_lee'] = dBFeatStat(data[1,:,:],datamask)
        if featSelection[9]==1:
            #print(' LEE coherence:')
            COH_lee = np.sqrt(np.add(np.square(data[2,:,:]),np.square(data[3,:,:])))/np.sqrt(data[1,:,:]*data[0,:,:])
            COH_lee, stat['COH_lee'] = featStat(COH_lee,datamask)
        if featSelection[10]==1:
            PHA_lee = np.cos(np.arctan2(data[3,:,:],data[2,:,:]))
            PHA_lee, stat['PHA_lee'] = featStat(PHA_lee,datamask)

    data = np.zeros([np.sum(featSelection),data.shape[1],data.shape[2]])
    orderChl = 0
    if featSelection[0]==1:
        data[orderChl,:,:] = VH_dB_un
        orderChl = orderChl + 1
        del(VH_dB_un)
    if featSelection[1]==1:
        data[orderChl,:,:] = VV_dB_un
        orderChl = orderChl + 1
        del(VV_dB_un)
    if featSelection[2]==1:
        data[orderChl,:,:] = COH_boxcar
        orderChl = orderChl + 1
        del(COH_boxcar)
    if featSelection[3]==1:
        data[orderChl,:,:] = VH_real
        orderChl = orderChl + 1
        del(VH_real)
    if featSelection[4]==1:
        data[orderChl,:,:] = VH_imag
        orderChl = orderChl + 1
        del(VH_imag)
    if featSelection[5]==1:
        data[orderChl,:,:] = VV_real
        orderChl = orderChl + 1
        del(VV_real)
    if featSelection[6]==1:
        data[orderChl,:,:] = VV_imag
        orderChl = orderChl + 1
        del(VV_imag)
    if featSelection[7]==1:
        data[orderChl,:,:] = VH_dB_lee
        orderChl = orderChl + 1
        del(VH_dB_lee)
    if featSelection[8]==1:
        data[orderChl,:,:] = VV_dB_lee
        orderChl = orderChl + 1
        del(VV_dB_lee)
    if featSelection[9]==1:
        data[orderChl,:,:] = COH_lee
        orderChl = orderChl + 1
        del(COH_lee)
    if featSelection[10]==1:
        data[orderChl,:,:] = PHA_lee
        orderChl = orderChl + 1
        del(PHA_lee)

    return data,datamask,stat

def getPath2LCZTIFF(dataPath, labelPath):
    city = dataPath.split('/')[-4].split('_')[-1].lower()
    gtPath = labelPath + '/' + city + '/' + city + '_lcz_GT.tif'
    return gtPath

def getPath2LCZ42v3(dataPath,labelPath):
    city = dataPath.split('/')[-4].split('_')[-1].lower()
    gtPath = labelPath + '/' + city + '_lcz_GT.tif'
    return gtPath

def urbanPCAAlign(data,datamask,stat):
    # dB thresholding
    dBThreshold = -5
    # find the channel of lee filtered vh in dB
    k = stat.keys()
    vhLeeIdx = 0
    if 'VHdB' in k:
        vhLeeIdx = vhLeeIdx + 1
    if 'VVdB' in k:
        vhLeeIdx = vhLeeIdx + 1
    if 'coh' in k:
        vhLeeIdx = vhLeeIdx + 1
    if 'VH_real' in k:
        vhLeeIdx = vhLeeIdx + 1
    if 'VH_imag' in k:
        vhLeeIdx = vhLeeIdx + 1
    if 'VV_real' in k:
        vhLeeIdx = vhLeeIdx + 1
    if 'VV_imag' in k:
        vhLeeIdx = vhLeeIdx + 1
    VHdBLee = data[vhLeeIdx,:,:]
    # masking data of urban
    mask = (datamask*1*((VHdBLee>dBThreshold)*1))==1
    urbanData = np.transpose(data[:,mask])
    # shifting data by median
    featMedian = np.median(urbanData,axis=0)
    featMedian = np.tile(featMedian,urbanData.shape[0])
    featMedian = np.reshape(featMedian,urbanData.shape)
    urbanData = urbanData - featMedian

    # pca projections
    from sklearn.decomposition import PCA
    pca = PCA()
    pca.fit(urbanData)

    # projection data of the whole city
    # step 1: median shift
    dn,rw,cl = data.shape
    data = np.transpose(data,(1,2,0))
    data = np.reshape(data,(rw*cl,dn))
    featMedian = featMedian[0,:]
    featMedian = np.tile(featMedian,data.shape[0])
    featMedian = np.reshape(featMedian,data.shape)
    data = data - featMedian
    # step 2: projection
    dataPCA = pca.transform(data)
    dataPCA = np.reshape(dataPCA,(rw,cl,dn))
    dataPCA = np.transpose(dataPCA,(2,0,1))

    print (dataPCA.shape)
    statPCA = []
    for i in range(0,dataPCA.shape[0]):
        statPCA.append({'mean':np.mean(dataPCA[i,:,:]),'std':np.std(dataPCA[i,:,:]),'median':np.median(dataPCA[i,:,:])})


    return dataPCA, statPCA

def getDataNormMStd(dataPath, featSelection = [0,0,0,0,0,0,0,0,0,0,0]):


    # featSelection: a 1 by 11 vector indicating which features should be extract.
    #
    # e.g. [1,1,0,1,1,1,0] means extract 5 features: VH_dB_un, VV_dB_un, VH_dB_un, VV_dB_un and COH_lee
    # by now, feature selection only support in total 7 features,
    # ------------------------------------------------------------------------------------
    #           Feature                 |    Shortcuts  |  delete code  |  preserving code
    # ------------------------------------------------------------------------------------
    #       unfiltered VH in dB         |    VH_dB_un   |      0        |        1
    #       unfiltered VV in dB         |    VV_dB_un   |      0        |        1
    #       boxcar coherence            |    COH_boxcar |      0        |        1
    #       VH real part                |    VH_real    |      0        |        1
    #       VH imag part                |    VH_imag    |      0        |        1
    #       VV real part                |    VV_real    |      0        |        1
    #       VV imag part                |    VV_imag    |      0        |        1
    #       lee-filtered VH in dB       |    VH_dB_lee  |      0        |        1
    #       lee-filtered VV in dB       |    VV_dB_lee  |      0        |        1
    #       lee-filtered coherence      |    COH_lee    |      0        |        1
    #       lee-filtered relative phase |    PHA_lee    |      0        |        1
    # -------------------------------------------------------------------------------------
    #
    #
    # dataPath = '/data/hu/LCZ42_SEN1/LCZ42_23052_LosAngeles-LongBeach-SantaAna/mosaic_unfilt_dat/201706/mosaic.tif'
    # featSelection = [1,1,0,1,1,1,0]
    # if featSelection = [0,0,0,0,0,0,0] return data mask and unfiltered data


    # generate data mask from lee-filtered data
    maskPath = dataPath.replace('unfilt_','')
    try:
        #print(maskPath)
        maskTif = gdal.Open(maskPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given data geotiff can not be open by GDAL")
        print("DIRECTORY:       "+dataPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    data = maskTif.ReadAsArray()
    # data mask extraction
    datamask = (data[0,:,:]+data[3,:,:])>0
    del(maskTif)
    del(data)


    # initial a dictionary to save maximum, minimum, histogram of intensity bands
    stat = {}

    # unfiltered data need to be loaded
    if np.sum(featSelection[:7]) > 0:
        try:
            dataTif = gdal.Open(dataPath)
        except RuntimeError as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("ERROR:           the given data geotiff can not be open by GDAL")
            print("DIRECTORY:       "+dataPath)
            print("GDAL EXCEPCTION: "+e)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sys.exit(1)
        # read data
        data = dataTif.ReadAsArray()
        data[np.isnan(data)] = 0
        VH_real = data[0,:,:].copy()
        VH_imag = data[1,:,:].copy()
        VV_real = data[2,:,:].copy()
        VV_imag = data[3,:,:].copy()

        # convert complex form into covariance matrix form
        tempData = np.zeros(data.shape)
        tempData[0,:,:] = data[0,:,:]*data[0,:,:] + data[1,:,:]*data[1,:,:]
        tempData[1,:,:] = data[2,:,:]*data[2,:,:] + data[3,:,:]*data[3,:,:]
        tempData[2,:,:] = data[0,:,:]*data[2,:,:] + data[1,:,:]*data[3,:,:]
        tempData[3,:,:] = data[1,:,:]*data[2,:,:] - data[0,:,:]*data[3,:,:]
        data = tempData
        del(tempData)

        # get intensity of VV, VH; get boxcar coherence
        VH_dB_un = data[0,:,:]
        VV_dB_un = data[1,:,:]
        data = boxcar(data,1)
        VH_dB_un[VH_dB_un==0] = data[0,VH_dB_un==0]
        VV_dB_un[VV_dB_un==0] = data[1,VV_dB_un==0]
        COH_boxcar = np.sqrt(np.add(np.square(data[2,:,:]),np.square(data[3,:,:])))/np.sqrt(data[1,:,:]*data[0,:,:])
        del(data)

        # convert intensity into dB, and normalization
        if featSelection[0]==1:
            #print(' unfiltered VH:')
            VH_dB_un, stat['VHdB'] = dBFeatStat(VH_dB_un,datamask)
        else:
            del(VH_dB_un)

        if featSelection[1]==1:
            #print(' unfiltered VV:')
            VV_dB_un, stat['VVdB'] = dBFeatStat(VV_dB_un,datamask)
        else:
            del(VV_dB_un)

        if featSelection[2]==1:
            #print(' boxcar coherence:')
            COH_boxcar, stat['coh'] = featStat(COH_boxcar,datamask)
        else:
            del(COH_boxcar)

        if featSelection[3]==1:
            #print(' VH real part:')
            VH_real, stat['VH_real'] = realImagFeatStat(VH_real,datamask)
        else:
            del(VH_real)
        if featSelection[4]==1:
            #print(' VH imaginary part:')
            VH_imag, stat['VH_imag'] = realImagFeatStat(VH_imag,datamask)
        else:
            del(VH_imag)
        if featSelection[5]==1:
            #print(' VV real part:')
            VV_real, stat['VV_real'] = realImagFeatStat(VV_real,datamask)
        else:
            del(VV_real)
        if featSelection[6]==1:
            #print(' VV imaginary part:')
            VV_imag, stat['VV_imag'] = realImagFeatStat(VV_imag,datamask)
        else:
            del(VV_imag)


        del(dataTif)

    if np.sum(featSelection[7:]) > 0:
        # lee-filtered data need to be loaded
        dataPath = dataPath.replace('unfilt_','')
        try:
            dataTif = gdal.Open(dataPath)
        except RuntimeError as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("ERROR:           the given data geotiff can not be open by GDAL")
            print("DIRECTORY:       "+dataPath)
            print("GDAL EXCEPCTION: "+e)
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            sys.exit(1)

        data = dataTif.ReadAsArray()

        data = np.stack((data[0,:,:],data[3,:,:],data[1,:,:],data[2,:,:]))

        if featSelection[7]==1:
            #print(' LEE filtered VH:')
            VH_dB_lee, stat['VH_dB_lee'] = dBFeatStat(data[0,:,:],datamask)
        if featSelection[8]==1:
            #print(' LEE filtered VV:')
            VV_dB_lee, stat['VV_dB_lee'] = dBFeatStat(data[1,:,:],datamask)
        if featSelection[9]==1:
            #print(' LEE coherence:')
            COH_lee = np.sqrt(np.add(np.square(data[2,:,:]),np.square(data[3,:,:])))/np.sqrt(data[1,:,:]*data[0,:,:])
            COH_lee, stat['COH_lee'] = featStat(COH_lee,datamask)
        if featSelection[10]==1:
            PHA_lee = np.cos(np.arctan2(data[3,:,:],data[2,:,:]))
            PHA_lee, stat['PHA_lee'] = featStat(PHA_lee,datamask)

    data = np.zeros([np.sum(featSelection),data.shape[1],data.shape[2]])
    orderChl = 0
    if featSelection[0]==1:
        data[orderChl,:,:] = (VH_dB_un-stat['VHdB']['mean'])/stat['VHdB']['std']
        orderChl = orderChl + 1
        del(VH_dB_un)
    if featSelection[1]==1:
        data[orderChl,:,:] = (VV_dB_un-stat['VVdB']['mean'])/stat['VVdB']['std']
        orderChl = orderChl + 1
        del(VV_dB_un)
    if featSelection[2]==1:
        data[orderChl,:,:] = (COH_boxcar-stat['coh']['mean'])/stat['coh']['std']
        orderChl = orderChl + 1
        del(COH_boxcar)
    if featSelection[3]==1:
        data[orderChl,:,:] = (VH_real-stat['VH_real']['mean'])/stat['VH_real']['std']
        orderChl = orderChl + 1
        del(VH_real)
    if featSelection[4]==1:
        data[orderChl,:,:] = (VH_imag-stat['VH_imag']['mean'])/stat['VH_imag']['std']
        orderChl = orderChl + 1
        del(VH_imag)
    if featSelection[5]==1:
        data[orderChl,:,:] = (VV_real-stat['VV_real']['mean'])/stat['VV_real']['std']
        orderChl = orderChl + 1
        del(VV_real)
    if featSelection[6]==1:
        data[orderChl,:,:] = (VV_imag-stat['VV_imag']['mean'])/stat['VV_imag']['std']
        orderChl = orderChl + 1
        del(VV_imag)
    if featSelection[7]==1:
        data[orderChl,:,:] = (VH_dB_lee-stat['VH_dB_lee']['mean'])/stat['VH_dB_lee']['std']
        orderChl = orderChl + 1
        del(VH_dB_lee)
    if featSelection[8]==1:
        data[orderChl,:,:] = (VV_dB_lee-stat['VV_dB_lee']['mean'])/stat['VV_dB_lee']['std']
        orderChl = orderChl + 1
        del(VV_dB_lee)
    if featSelection[9]==1:
        data[orderChl,:,:] = (COH_lee-stat['COH_lee']['mean'])/stat['COH_lee']['std']
        orderChl = orderChl + 1
        del(COH_lee)
    if featSelection[10]==1:
        data[orderChl,:,:] = (PHA_lee-stat['PHA_lee']['mean'])/stat['PHA_lee']['std']
        orderChl = orderChl + 1
        del(PHA_lee)

    return data,datamask,stat



def getTrainData(dataPath, gtPath, featSelection = 0,patchSize = 32):
    # featSelection: a 1 by 11 vector indicating which features should be extract.
    #
    # e.g. [1,1,0,0,0,0,0,1,1,1,0] means extract 5 features: VH_dB_un, VV_dB_un, VH_dB_un, VV_dB_un and COH_lee
    # by now, feature selection only support in total 7 features,
    # ------------------------------------------------------------------------------------
    #           Feature                 |    Shortcuts  |  delete code  |  preserving code
    # ------------------------------------------------------------------------------------
    #       unfiltered VH in dB         |    VH_dB_un   |      0        |        1
    #       unfiltered VV in dB         |    VV_dB_un   |      0        |        1
    #       boxcar coherence            |    COH_boxcar |      0        |        1
    #       VH real part                |    VH_real    |      0        |        1
    #       VH imag part                |    VH_imag    |      0        |        1
    #       VV real part                |    VV_real    |      0        |        1
    #       VV imag part                |    VV_imag    |      0        |        1
    #       lee-filtered VH in dB       |    VH_dB_lee  |      0        |        1
    #       lee-filtered VV in dB       |    VV_dB_lee  |      0        |        1
    #       lee-filtered coherence      |    COH_lee    |      0        |        1
    #       lee-filtered relative phase |    PHA_lee    |      0        |        1
    # -------------------------------------------------------------------------------------
    #
    #
    # dataPath = '/media/sf_So2Sat/data/LCZ42_22606_Zurich/mosaic_unfilt_dat/201612/mosaic.tif'
    # gtPath = '/media/sf_So2Sat/LCZ42/zurich/zurich_lcz_GT.tif'
    # featSelection = [0,0,0,0,1,1,0]
    if np.sum(featSelection) == 0:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       No feature is selected")
        print("ERROR:       featSeletion = "+str(featSelection))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    # get data and nodata mask
    data, mask, stat = getData(dataPath, featSelection)

    # eliminate the data on the boundary
    mask[:np.int(np.floor(patchSize/2)),:] = False
    mask[-np.int(np.floor(patchSize/2)):,:] = False
    mask[:,:np.int(np.floor(patchSize/2))] = False
    mask[:,-np.int(np.floor(patchSize/2)):] = False


    col_dat,row_dat,xWorld,yWorld,row_lab,col_lab = getCoordinate(gtPath,dataPath)
    coord = np.stack((row_dat,col_dat,xWorld,yWorld,row_lab,col_lab),axis=1)
    del col_dat,row_dat,xWorld,yWorld,row_lab,col_lab

    # read label data and find data corresponds to label location
    labelTif = gdal.Open(gtPath)
    label = labelTif.ReadAsArray()
    label[label<0] = 0
    label[label>100] = label[label>100]-90

    # delete those labels on boundary or in no data area
    coord = coordInMask(coord, mask, patchSize)
    row_dat = coord[:,0].astype(np.int)
    col_dat = coord[:,1].astype(np.int)
    row_lab = coord[:,4].astype(np.int)
    col_lab = coord[:,5].astype(np.int)



    # cutting patches
    trainDat = np.zeros([len(row_dat),patchSize,patchSize,data.shape[0]])
    trainLab = np.zeros([len(row_dat),17])

    for idx in range(0,len(row_dat)):
        trainDat[idx,:,:,:] = np.transpose(data[:,int(row_dat[idx]-patchSize/2):int(row_dat[idx]+patchSize/2),int(col_dat[idx]-patchSize/2):int(col_dat[idx]+patchSize/2)],(1,2,0))
        trainLab[idx,int(label[row_lab[idx],col_lab[idx]]-1)] = 1

    return trainDat, trainLab, coord, stat



def cutPatches(imagRow,imagCol,data,patchSize):
    # this function cut patches from data
    # Input
    # 	- imagRow 	-- image row location of patch centers
    #   - imagCol	-- image col location of patch centers
    #   - data 		-- data to be cut [dn,rw,cl]
    #	- patchSize 	-- size of patch
    #
    # Output
    #	- dat 		-- data patches in [nb,rw,cl,dn]; nb: number of patches, rw: row of pathces, cl: cl of patches, dn: dimension of patches


    dat = np.zeros([len(imagRow),patchSize,patchSize,data.shape[0]])
    for idx in range(0,len(imagRow)):
        dat[idx,:,:,:] = np.transpose(data[:,int(imagRow[idx]-patchSize/2):int(imagRow[idx]+patchSize/2),int(imagCol[idx]-patchSize/2):int(imagCol[idx]+patchSize/2)],(1,2,0))
    return dat



def getTrainTestData(dataPath, trainMapPath, testMapPath, featSelection = [1,1,1,1,1,1,1,1,1,1,1], patchSize = 32):
    # featSelection: a 1 by 7 vector indicating which features should be extract.
    #
    # e.g. [1,1,0,1,1,1,0] means extract 5 features: VH_dB_un, VV_dB_un, VH_dB_un, VV_dB_un and COH_lee
    # by now, feature selection only support in total 7 features,
    # ------------------------------------------------------------------------------------
    #           Feature                 |    Shortcuts  |  delete code  |  preserving code
    # ------------------------------------------------------------------------------------
    #       unfiltered VH in dB         |    VH_dB_un   |      0        |        1
    #       unfiltered VV in dB         |    VV_dB_un   |      0        |        1
    #       boxcar coherence            |    COH_boxcar |      0        |        1
    #       VH real part                |    VH_real    |      0        |        1
    #       VH imag part                |    VH_imag    |      0        |        1
    #       VV real part                |    VV_real    |      0        |        1
    #       VV imag part                |    VV_imag    |      0        |        1
    #       lee-filtered VH in dB       |    VH_dB_lee  |      0        |        1
    #       lee-filtered VV in dB       |    VV_dB_lee  |      0        |        1
    #       lee-filtered coherence      |    COH_lee    |      0        |        1
    #       lee-filtered relative phase |    PHA_lee    |      0        |        1
    # -------------------------------------------------------------------------------------
    #
    #
    # dataPath = '/media/sf_So2Sat/data/LCZ42_22606_Zurich/mosaic_unfilt_dat/201612/mosaic.tif'
    # gtPath = '/media/sf_So2Sat/LCZ42/zurich/zurich_lcz_GT.tif'
    # featSelection = [0,0,0,0,1,1,0]
    if np.sum(featSelection) == 0:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:       No feature is selected")
        print("ERROR:       featSeletion = "+str(featSelection))
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    # get data and data mask
    data, mask, stat = getData(dataPath, featSelection)

    # eliminate the data on the boundary
    mask[:np.int(np.floor(patchSize/2)),:] = False
    mask[-np.int(np.floor(patchSize/2)):,:] = False
    mask[:,:np.int(np.floor(patchSize/2))] = False
    mask[:,-np.int(np.floor(patchSize/2)):] = False


    # load training data based on training map
    col_dat,row_dat,xWorld,yWorld,row_lab,col_lab = getCoordinate(trainMapPath,dataPath)
    trainCoord = np.stack((row_dat,col_dat,xWorld,yWorld,row_lab,col_lab),axis=1)
    del col_dat,row_dat,xWorld,yWorld,row_lab,col_lab


    # read label data and find data corresponds to label location
    labelTif = gdal.Open(trainMapPath)
    label = labelTif.ReadAsArray()
    label[label<0] = 0
    label[label>100] = label[label>100]-90

    # delete those labels on boundary or in no data area
    trainCoord = coordInMask(trainCoord, mask, patchSize)
    row_dat = trainCoord[:,0].astype(np.int)
    col_dat = trainCoord[:,1].astype(np.int)
    row_lab = trainCoord[:,4].astype(np.int)
    col_lab = trainCoord[:,5].astype(np.int)

    # cutting patches
    trainDat = np.zeros([len(row_dat),patchSize,patchSize,data.shape[0]])
    trainLab = np.zeros([len(row_dat),17])

    for idx in range(0,len(row_dat)):
        trainDat[idx,:,:,:] = np.transpose(data[:,int(row_dat[idx]-patchSize/2):int(row_dat[idx]+patchSize/2),int(col_dat[idx]-patchSize/2):int(col_dat[idx]+patchSize/2)],(1,2,0))
        trainLab[idx,int(label[row_lab[idx],col_lab[idx]]-1)] = 1

    del(labelTif)


    # load testing data based on tesing map
    col_dat,row_dat,xWorld,yWorld,row_lab,col_lab = getCoordinate(testMapPath,dataPath)
    testCoord = np.stack((row_dat,col_dat,xWorld,yWorld,row_lab,col_lab),axis=1)
    del col_dat,row_dat,xWorld,yWorld,row_lab,col_lab

    # read label data and find data corresponds to label location
    labelTif = gdal.Open(testMapPath)
    label = labelTif.ReadAsArray()
    label[label<0] = 0
    label[label>100] = label[label>100]-90

    # delete those labels on boundary or in no data area
    testCoord = coordInMask(testCoord,mask,patchSize)
    row_dat = testCoord[:,0].astype(np.int)
    col_dat = testCoord[:,1].astype(np.int)
    row_lab = testCoord[:,4].astype(np.int)
    col_lab = testCoord[:,5].astype(np.int)


    # cutting patches
    testDat = np.zeros([len(row_dat),patchSize,patchSize,data.shape[0]])
    testLab = np.zeros([len(row_dat),17])

    for idx in range(0,len(row_dat)):
        testDat[idx,:,:,:] = np.transpose(data[:,int(row_dat[idx]-patchSize/2):int(row_dat[idx]+patchSize/2),int(col_dat[idx]-patchSize/2):int(col_dat[idx]+patchSize/2)],(1,2,0))
        testLab[idx,int(label[row_lab[idx],col_lab[idx]]-1)] = 1

    return trainDat, trainLab, trainCoord, testDat, testLab, testCoord, stat


def coordInMask(coord,datamask,patchSize):

    out_coord = coord.copy()

    # delete label on northern boundary
    row_dat = out_coord[:,0].copy()
    idxBoundary = np.where(row_dat<np.floor(patchSize/2))
    out_coord = np.delete(out_coord,idxBoundary,0)

    # delete label on southern boundary
    row_dat = out_coord[:,0].copy()
    idxBoundary = np.where(row_dat>(datamask.shape[0]-np.floor(patchSize/2)-1))
    out_coord = np.delete(out_coord,idxBoundary,0)

    # delete label on western boundary
    col_dat = out_coord[:,1].copy()
    idxBoundary = np.where(col_dat<np.floor(patchSize/2))
    out_coord = np.delete(out_coord,idxBoundary,0)

    # delete label on eastern boundary
    col_dat = out_coord[:,1].copy()
    idxBoundary = np.where(col_dat>(datamask.shape[1]-np.floor(patchSize/2)-1))
    out_coord = np.delete(out_coord,idxBoundary,0)


    # delete label in no data area
    row_dat = out_coord[:,0].copy()
    col_dat = out_coord[:,1].copy()

    idx = len(row_dat)-1
    for row_val in reversed(row_dat):
        if datamask[int(row_val-patchSize/2):int(row_val+patchSize/2),int(col_dat[idx]-patchSize/2):int(col_dat[idx]+patchSize/2)].all()==False:
            row_dat = np.delete(row_dat,idx,0)
            col_dat = np.delete(col_dat,idx,0)
            out_coord = np.delete(out_coord,idx,0)
        idx = idx - 1

    return out_coord


def readH5DataPatches(cityList,dataStorePath,featSelection = [0,1,2,7,8,9,10]):
# cityList = ['vancouver']
# dataStorePath = '/data/hu/LCZ42_SEN1_H5_RANDOM_Feat11'

    # read patch size
    fid = h5py.File(dataStorePath + '/' + cityList[0] + '/' + cityList[0] + '.h5','r')
    _,patchSize,_,_ = fid['x_tra'].shape
    del fid

    # initial data
    x_tra  = np.empty(shape=[1,patchSize,patchSize,len(featSelection)])
    y_tra  = np.zeros([1,17])

    # read data of the city list
    for i in range(0,len(cityList)):
        city = cityList[i]
        print('Loading data of the city: '+city)
        h5filePath = dataStorePath + '/' + city + '/' + city + '.h5'
        fid = h5py.File(h5filePath,'r')

        if fid['x_test'].shape[0]==0:
            x_tmp = fid['x_tra'][:,:,:,featSelection]
            y_tmp = fid['y_tra'][:]
        else:
            tempA = fid['x_tra'][:,:,:,featSelection]
            tempB = fid['x_test'][:,:,:,featSelection]
            x_tmp = np.concatenate((tempA,tempB),axis=0)
            del tempA, tempB
            tempA = fid['y_tra'][:]
            tempB = fid['y_test'][:]
            y_tmp = np.concatenate((tempA,tempB),axis=0)
            del tempA,tempB
        fid.close
        del fid
        x_tra  = np.concatenate((x_tra,x_tmp),axis=0)
        y_tra  = np.concatenate((y_tra,y_tmp),axis=0)

    # delete the first element which is used to initialize x_tra and y_tra
    x_tra = np.delete(x_tra, (0), axis=0)
    y_tra = np.delete(y_tra, (0), axis=0)

    return x_tra, y_tra
