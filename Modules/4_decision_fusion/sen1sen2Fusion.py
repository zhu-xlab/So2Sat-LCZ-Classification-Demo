"""
Created on Tue 07.01.2020 11:32:08
@author: hu jingliang, qiu chunping
Current issue (16-03-2020): the image size of s1 and s2 are different for now. check again after the latest 1700 processing is done
"""
# Last modified: 27.03.2020 20:07:39 Yuanyuan Wang
# modified input output path, and SEN2 LCZ result path


import os
import osr
import gdal
import numpy as np
import sys
sys.path.insert(1, '../Classification')

import sen1_cnntrain_uil as sen1cnn
import glob2
"""
1. inputs:
	- path2Sen1OfCity		-- the directory to the sentinel-1 data of the city under processing
	- path2Sen2OfCity               -- the directory to the sentinel-2 data of the city under processing
"""

#path2Sen1OfCity = '/data/hu/so2sat_CNN/test_data/s1/00012_22044_Karachi'
path2Sen1OfCity = sys.argv[1]

#path2Sen2OfCity = '/data/hu/so2sat_CNN/test_data/s2/00012_22044_Karachi'
path2Sen2OfCity = sys.argv[2]


"""
2. load the sentinel-1 softmax outputs
"""
dataPathTime = sen1cnn.getPathOfTime(path2Sen1OfCity)
dataPathTif = os.path.join(dataPathTime[0] ,'mosaic.tif')
s1ProbTif = '/'.join(dataPathTif.split('/')[:-1])
s1ProbTif = s1ProbTif.replace('mosaic_unfilt_dat','LCZClaMap')+'/'+'LCZProb.tif'

try:
    f = gdal.Open(s1ProbTif)
except RuntimeError as e:
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print("ERROR:           the Sentinel-1 softmax geotiff can not be open by GDAL")
    print("DIRECTORY:       "+s1ProbTif)
    print("GDAL EXCEPCTION: ")
    print(e)
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    sys.exit(1)

sen1_row = f.RasterYSize
sen1_col = f.RasterXSize
sen1_epsg = osr.SpatialReference(wkt=f.GetProjection())
sen1_epsg = sen1_epsg.GetAttrValue('AUTHORITY',1)
sen1_softmax = np.single(f.ReadAsArray())
sen1_softmax[np.isnan(sen1_softmax)]=0
#print(sen1_softmax.shape)
sen1_geoInfo = f.GetGeoTransform()
sen1_proj = f.GetProjection()


del(f)



"""
3. load the sentinel-2 softmax outputs
"""
files = sorted(glob2.glob(path2Sen2OfCity +'/LCZ_ResNet20/*_pro.tiff'))
id=1
for fil in files:
    try:
        f = gdal.Open(fil)
    except RuntimeError as e:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("ERROR:           the Sentinel-2 softmax geotiff can not be open by GDAL")
        print("DIRECTORY:       "+fil)
        print("GDAL EXCEPCTION: ")
        print(e)
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        sys.exit(1)
    if id==1:
        sen2_softmax = np.single(f.ReadAsArray())
    else:
        sen2_softmax = sen2_softmax+np.single(f.ReadAsArray())
    id=id+1
print(sen2_softmax.shape)
sen2_row = f.RasterYSize
sen2_col = f.RasterXSize
sen2_epsg = osr.SpatialReference(wkt=f.GetProjection())
sen2_epsg = sen2_epsg.GetAttrValue('AUTHORITY',1)
sen2_geoInfo = f.GetGeoTransform()
sen2_proj = f.GetProjection()

del(f)

"""
4. check the alignment of the sentinel-1 and sentinel-2 softmax outputs
"""
if sen1_row != sen2_row:
    print("The number of rows of the softmax outputs are not equal")
    sys.exit(1)
elif sen1_col != sen2_col:
    print("The number of columns of the softmax outputs are not equal")
    sys.exit(1)
elif sen1_epsg != sen2_epsg:
    print("The EPSG code of the softmax outputs are not identical")
    sys.exit(1)


"""
5. fusion
"""
fusion_softmax = sen1_softmax + sen2_softmax
fusion_label = np.argmax(fusion_softmax,axis=0).astype(np.int16)+1


"""
6. save fusion results as geotiff
"""
fusionDir = '/'.join(s1ProbTif.split('/')[:-3])+'/LCZ_Fusion/'+s1ProbTif.split('/')[-2]
if not os.path.exists(fusionDir):
    os.makedirs(fusionDir)

fusionPath = fusionDir + "/s1_s2_fusion.tif"

LCZDriver = gdal.GetDriverByName('GTiff')
LCZFile = LCZDriver.Create(fusionPath, sen1_col, sen1_row, 1, gdal.GDT_UInt16)
LCZFile.SetProjection(sen1_proj)
LCZFile.SetGeoTransform(sen1_geoInfo)

outBand = LCZFile.GetRasterBand(1)
outBand.WriteArray(fusion_label)
outBand.FlushCache()
del(outBand)

print('INFO:    Fusion result is saved at: ', fusionPath)
#print(fusionPath)
