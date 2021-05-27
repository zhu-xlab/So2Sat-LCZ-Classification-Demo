"""
Created on Tue Jul 19 09:06:08 2019
@author: CQ
"""
# Last modified: 25.03.2020 22:08:37 Yuanyuan Wang
# debug to fit parallel processing

from __future__ import print_function
import os
import sys
import time
import logging
import numpy as np
import sen2_production_uil as sen2cnn
import _production_uil as gp

import tensorflow as tf
import resnet_v2

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'
os.environ["TF_ENABLE_AUTO_MIXED_PRECISION"] = "1"
config = tf.ConfigProto()
config.gpu_options.per_process_gpu_memory_fraction = 0.4
session = tf.Session(config=config)


"set the path to the multi-seasonal s2 data"
# path2DataOfCity = '/00017_22007_Lagos'#'
path2DataOfCity = sys.argv[1]
"set the path to the trained model"
# path2NetModel = '/P_52_A/S2_RESNET20_BS16_LR2e-4_IN32-32-10_PRO-52-0R12_2019-06-27T10:16:53+02:00.hdf5'
path2NetModel = sys.argv[2]

# 1. parameter setting
# patch size
patchsize = 32
# patch shape
patch_shape = (32, 32, 10)
# batch size
batch_size = 256


# 2. read data of a given city, patch cutting, and initial classification map tiff file
# read data path
image2processed=sen2cnn.createFileList(path2DataOfCity) ;
numImg=len(image2processed)
print("INFO:    Number of seasonal images: ", numImg)
print(numImg)

if numImg==0:
	sys.exit("no images found!")
city=path2DataOfCity[path2DataOfCity.rfind('/')+1:]


"process each of the multi-seasonal data and applying majority voting"
for idSeason in np.arange(numImg):
    dataPathTif = image2processed[idSeason]

    outProbTif = path2DataOfCity+'/LCZ_ResNet20/'+city+dataPathTif[dataPathTif.rfind('_'):-4]+'_pro.tiff'
    outLabelTif = outProbTif.replace('_pro','_lab')
    print('The directories of output:')
    #print(outProbTif)
    #print(outLabelTif)

    # initial classification map tiff file
    LCZProbPath = gp.initialLCZProbGrid(dataPathTif,outProbTif)

    # LCZLabelPath = gp.initialLCZLabelGrid(dataPathTif,outLabelTif)
    if idSeason==0:
        #file name of the mv results
        outLabelTif_mv = path2DataOfCity+'/LCZ_ResNet20/'+city+'_lab.tiff'
        LCZLabelPath = gp.initialLCZLabelGrid(dataPathTif,outLabelTif_mv)

    # get patch coordinate
    coordCell = gp.getCoordLCZGrid(outProbTif)
    coordImage = gp.getImageCoordByXYCoord(coordCell,dataPathTif)
    # read data and feature extraction
    dataFeature  = sen2cnn.getData(dataPathTif, [1,2,3,4,5,6,7,8,11,12], 10000.0)
    #print(dataFeature.shape)

    # cutting patches
    dataPatches = gp.getPatch(dataFeature, coordImage, patchsize)
    del dataFeature

    # 3. loading trained CNN and predict label
    model = resnet_v2.resnet_v2(input_shape=patch_shape, depth=20, num_classes = 17)
    timeStart = time.time()
    model.load_weights(path2NetModel)
    timeEnd = time.time()
    print('INFO:    TIME SPENT FOR LOADING TRAINED CNN MODEL IS: '+str(timeEnd-timeStart))

    probPred = model.predict(dataPatches, batch_size = batch_size)
    print('INFO:    Predition finished.')
    del dataPatches

    # 4. save predicted probability and label
    probPath = gp.saveProbabilityPrediction(probPred,outProbTif)

    if idSeason==0:
        probPred_all = probPred
    else:
        probPred_all = probPred_all + probPred

    del probPred

probPred_all=probPred_all/float(numImg)
probPath = sen2cnn.saveLabel_fromSoftmax(probPred_all, outLabelTif_mv)
