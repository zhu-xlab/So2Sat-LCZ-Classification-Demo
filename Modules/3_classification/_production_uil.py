"""
Created on Fri June 29 15:09:53 2018

@author: hu jingliang
"""

from __future__ import print_function
import os
import glob
import numpy as np
from osgeo import gdal
import sys
gdal.UseExceptions()

def saveProbabilityPrediction(probPred,tiffPath):
# this function save the predicted probabilities
    try:
        fid = gdal.Open(tiffPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given data geotiff can not be open by GDAL")
        print("DIRECTORY:       "+tiffPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    row = fid.RasterYSize
    col = fid.RasterXSize
    bnd = fid.RasterCount
    proj = fid.GetProjection()
    geoInfo = fid.GetGeoTransform()
    del(fid)

    if probPred.shape[0] != row * col:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           number of patches does not suit the output size")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    print(np.median(probPred[:]))
    probPred = np.array(probPred*1e4)
    print(np.median(probPred[:]))
    probPred = probPred.astype(np.int16)
    print(np.median(probPred[:]))
    print(probPred.shape)
    prob = np.transpose(np.reshape(probPred,(row,col,17)),(2,0,1))
    print(probPred.shape)


    LCZDriver = gdal.GetDriverByName('GTiff')
    LCZFile = LCZDriver.Create(tiffPath, col, row, bnd, gdal.GDT_UInt16)
    LCZFile.SetProjection(proj)
    LCZFile.SetGeoTransform(geoInfo)

    # save file with int zeros
    idBnd = np.arange(0,bnd,dtype=int)
    for idxBnd in idBnd:
        outBand = LCZFile.GetRasterBand(int(idxBnd+1))
        outBand.WriteArray(prob[idxBnd,:,:].astype(np.int16))
        outBand.FlushCache()
        del(outBand)

    return tiffPath




def saveLabelPrediction(labPred,tiffPath):
# this function save the predicted label
    try:
        fid = gdal.Open(tiffPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given data geotiff can not be open by GDAL")
        print("DIRECTORY:       "+tiffPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    row = fid.RasterYSize
    col = fid.RasterXSize
    bnd = fid.RasterCount
    proj = fid.GetProjection()
    geoInfo = fid.GetGeoTransform()
    del(fid)

    if labPred.shape[0] != row * col:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           number of patches does not suit the output size")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    print(labPred.shape)
    print(np.median(labPred[:]))
    lab = np.reshape(labPred,(row,col))+1
#    lab = prob.argmax(axis=2).astype(np.uint8)+1
    print(lab.shape)
    print(np.median(lab[:]))


    LCZDriver = gdal.GetDriverByName('GTiff')
    LCZFile = LCZDriver.Create(tiffPath, col, row, bnd, gdal.GDT_UInt16)
    LCZFile.SetProjection(proj)
    LCZFile.SetGeoTransform(geoInfo)

    # save file with predicted label
    outBand = LCZFile.GetRasterBand(1)
    outBand.WriteArray(lab)
    outBand.FlushCache()
    del(outBand)

    return tiffPath





def getPatch(data,imageCoord,patchsize):
# this function gets data patch with give image coordinate and patch size
    halfPatchSize = np.int(np.floor(patchsize/2))

    outData = np.lib.pad(data,((0,0),(halfPatchSize,halfPatchSize),(halfPatchSize,halfPatchSize)),'symmetric')
    outData = np.transpose(outData,(1,2,0))

    imageCoord = imageCoord + halfPatchSize

    print('INFO:    Array size: ' + str(imageCoord.shape[0]) + ',' + str(patchsize) + ',' + str(patchsize) + ',' + str(data.shape[0]))
    dataPatch = np.zeros((imageCoord.shape[0], patchsize,patchsize,data.shape[0]), dtype=np.float32)

    for i in range(0,imageCoord.shape[0]):
        #print(i)
        dataPatch[i,:,:,:] = outData[imageCoord[i,1]-halfPatchSize:imageCoord[i,1]+halfPatchSize,imageCoord[i,0]-halfPatchSize:imageCoord[i,0]+halfPatchSize,:]

    return dataPatch



def getImageCoordByXYCoord(coord,path2Data):
# this function gets data patches by given coordinates
# Input:
#         - coord           -- coordinate [x,y]
#         - path2Data       -- path to unfiltered tiff data
#
# Output:
#         - imageCoord      -- image coordinate of the input real world coordiate
#


    try:
        fid = gdal.Open(path2Data)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given ground truth geotiff can not be open by GDAL")
        print("DIRECTORY:       "+gtPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)


    geoInfoData = fid.GetGeoTransform()

    imageCoord = np.zeros(coord.shape)

    imageCoord[:,0] = np.round((coord[:,0] - geoInfoData[0])/geoInfoData[1])
    imageCoord[:,1] = np.round((geoInfoData[3] - coord[:,1])/np.abs(geoInfoData[5]))

    return imageCoord.astype(int)


def getCoordLCZGrid(lczPath):
# this function gets the coordinate of every cell for the LCZ classification map
# Input:
#         - lczPath         -- path to a initialed lcz classification map grid
#
# Output:
#         - coordCell       -- the coordinate of each cell of the map grid. A N by 2 array with N is the number of cell, 1st col is x-coordinate, 2nd col is y-coordinate, The coordinate organized line by line.
#

    try:
        fid = gdal.Open(lczPath)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the given ground truth geotiff can not be open by GDAL")
        print("DIRECTORY:       "+gtPath)
        print("GDAL EXCEPCTION: "+e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)

    # read the grid and find coordinate of each cell
    row_cell = np.arange(0,fid.RasterYSize)
    col_cell = np.arange(0,fid.RasterXSize)

    geoInfoGrid = fid.GetGeoTransform()

    xWorld = geoInfoGrid[0] + col_cell * geoInfoGrid[1];
    yWorld = geoInfoGrid[3] + row_cell * geoInfoGrid[5];

    [xWorld,yWorld] = np.meshgrid(xWorld,yWorld)
    coordCell = np.transpose(np.stack((np.ravel(xWorld),np.ravel(yWorld)),axis=0))
    return coordCell






def initialLCZGrids(tiffData):
# this function initial a LCZ label grid and a LCZ probability grid.
#    Input:
#        - tiffData        -- path to sentinel-1 tiff data
#                          -- EXAMPLE: tiffData = '/data/hu/global_processing/01692_22142_Katowice/geocoded_subset_unfilt_dat/201706/S1B_IW_SLC__1SDV_20170601T045205_20170601T045232_005852_00A42A_504B_Orb_Cal_Deb_TC_SUB.tif'
#
#    Output:
#        - return 0        -- a LCZ tiff initialized
#                          -- EXAMPLE:
#
    # number of bands, number of LCZ classes
    nbBnd = 17

    # read geoinformation from the sentinel-1 tiff data
    dataFile = gdal.Open(tiffData)
    dataCoordSys = np.array(dataFile.GetGeoTransform())
    dataCol = dataFile.RasterXSize
    dataRow = dataFile.RasterYSize

    # set geoinformation for the output LCZ label grid
    # set resolution and coordinate for upper-left point
    LCZCoordSys = dataCoordSys.copy()
    LCZCoordSys[1] = 100
    LCZCoordSys[5] = -100
    LCZCol = np.arange(dataCoordSys[0],dataCoordSys[0]+dataCol*dataCoordSys[1],LCZCoordSys[1]).shape[0]
    LCZRow = np.arange(dataCoordSys[3],dataCoordSys[3]+dataRow*dataCoordSys[5],LCZCoordSys[5]).shape[0]

    # set the directory of initial grid
    savePath = '/'.join(tiffData.split('/')[:-1])
    savePath = savePath.replace(tiffData.split('/')[-3],'LCZClaMap')
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    # initial the grid and set resolution, projection, and coordinate
    LCZDriver = gdal.GetDriverByName('GTiff')
    LCZTiffPath = savePath+'/LCZLabel.tif'
    LCZFile = LCZDriver.Create(savePath+'/LCZLabel.tif', LCZCol, LCZRow)
    LCZFile.SetProjection(dataFile.GetProjection())
    LCZFile.SetGeoTransform(LCZCoordSys)

    # save file with int zeros
    LCZLabel = np.zeros((LCZRow,LCZCol),dtype = int)
    outBand = LCZFile.GetRasterBand(1)
    outBand.WriteArray(LCZLabel)
    outBand.FlushCache()

    del(LCZDriver)
    del(LCZFile)
    del(outBand)
    del(LCZLabel)


    # initial the grid and set resolution, projection, and coordinate
    LCZDriver = gdal.GetDriverByName('GTiff')
    LCZFile = LCZDriver.Create(savePath+'/LCZProb.tif', LCZCol, LCZRow, nbBnd)
    LCZFile.SetProjection(dataFile.GetProjection())
    LCZFile.SetGeoTransform(LCZCoordSys)

    # save file with int zeros
    LCZLabel = np.zeros((LCZRow,LCZCol))
    idBnd = np.arange(0,nbBnd,dtype=int)
    for idxBnd in idBnd:
        outBand = LCZFile.GetRasterBand(idxBnd+1)
        outBand.WriteArray(LCZLabel)
        outBand.FlushCache()
        del(outBand)
    outputpath = [savePath+'/LCZLabel.tif',savePath+'/LCZProb.tif']

    return outputpath





def initialLCZLabelGrid(tiffData,outGridDir):
# this function initial a 100 meter resolution LCZ label grid based on input geotiff.
#    Input:
#        - tiffData        -- path to sentinel-1 or senitnel-2 tiff data
# 	 - outGridDir      -- path to initialed lcz label geotiff
#
#    Output:
#        - return 0        -- a LCZ tiff initialized
    # read geoinformation from the sentinel-1 tiff data
    dataFile = gdal.Open(tiffData)
    dataCoordSys = np.array(dataFile.GetGeoTransform())
    dataCol = dataFile.RasterXSize
    dataRow = dataFile.RasterYSize

    # set geoinformation for the output LCZ label grid
    # set resolution and coordinate for upper-left point
    LCZCoordSys = dataCoordSys.copy()
    LCZCoordSys[1] = 100
    LCZCoordSys[5] = -100
    LCZCol = np.arange(dataCoordSys[0],dataCoordSys[0]+dataCol*dataCoordSys[1],LCZCoordSys[1]).shape[0]
    LCZRow = np.arange(dataCoordSys[3],dataCoordSys[3]+dataRow*dataCoordSys[5],LCZCoordSys[5]).shape[0]

    # set the directory of initial grid
    savePath = '/'.join(outGridDir.split('/')[:-1])
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    # initial the grid and set resolution, projection, and coordinate
    LCZDriver = gdal.GetDriverByName('GTiff')
    LCZFile = LCZDriver.Create(outGridDir, LCZCol, LCZRow)
    LCZFile.SetProjection(dataFile.GetProjection())
    LCZFile.SetGeoTransform(LCZCoordSys)

    # save file with int zeros
    LCZLabel = np.zeros((LCZRow,LCZCol),dtype = np.int8)
    outBand = LCZFile.GetRasterBand(1)
    outBand.WriteArray(LCZLabel)
    outBand.FlushCache()
    return 0

def initialLCZProbGrid(tiffData,outGridDir):
# this function initial a 100 meter resolution LCZ label grid based on input geotiff.
#    Input:
#        - tiffData        -- path to sentinel-1 or sentinel-2 tiff data
# 	 - outGridDir      -- path to initialized softmax geotiff file
#
#    Output:
#        - return 0        -- a LCZ tiff initialized with 17 bands, each of them presents a probability that the pixel falls under a class
#                          -- EXAMPLE:
#
    # number of bands, number of LCZ classes
    nbBnd = 17
    # read geoinformation from the sentinel-1 tiff data
    dataFile = gdal.Open(tiffData)
    dataCoordSys = np.array(dataFile.GetGeoTransform())
    dataCol = dataFile.RasterXSize
    dataRow = dataFile.RasterYSize

    # set geoinformation for the output LCZ label grid
    # set resolution and coordinate for upper-left point
    LCZCoordSys = dataCoordSys.copy()
    LCZCoordSys[1] = 100
    LCZCoordSys[5] = -100
    LCZCol = np.arange(dataCoordSys[0],dataCoordSys[0]+dataCol*dataCoordSys[1],LCZCoordSys[1]).shape[0]
    LCZRow = np.arange(dataCoordSys[3],dataCoordSys[3]+dataRow*dataCoordSys[5],LCZCoordSys[5]).shape[0]

    # set the directory of initial grid
    savePath = '/'.join(outGridDir.split('/')[:-1])
    if not os.path.exists(savePath):
        os.makedirs(savePath)

    # initial the grid and set resolution, projection, and coordinate
    LCZDriver = gdal.GetDriverByName('GTiff')
    LCZFile = LCZDriver.Create(outGridDir, LCZCol, LCZRow, nbBnd)
    LCZFile.SetProjection(dataFile.GetProjection())
    LCZFile.SetGeoTransform(LCZCoordSys)

    # save file with int zeros
    LCZProb = np.zeros((LCZRow,LCZCol),dtype = np.int16)
    nbBnd = 17
    idBnd = np.arange(0,nbBnd,dtype=int)
    for idxBnd in idBnd:
        outBand = LCZFile.GetRasterBand(int(idxBnd+1))
        outBand.WriteArray(LCZProb)
        outBand.FlushCache()
        del(outBand)

    return 0
