#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File              : /home/wang/processor/s1p/ma_data_proc_leeflt_3.0/python_scripts/global_production.py
# Date              : 10.04.2020 00:18:06
# Last Modified Date: 10.04.2020 00:18:06
# Last Modified By  : Yuanyuan Wang <y.wang@tum.de>
"""
Created on Tue Jun 29 09:06:08 2018
@author: hu jingliang
"""
# Last modified: 19.03.2020 21:01:25 Yuanyuan Wang
# modified GPU index

# Last modified: 10.04.2020 00:18:26 Yuanyuan Wang
# commented out printing messages 

# Last modified: 10.04.2020 00:18:48 Yuanyuan Wang
# changed 

import os
import sys
import time
import logging
import tensorflow as tf
import numpy as np
import sen1_cnntrain_uil as sen1cnn
import sen1_production_uil as gp
# import se1Processing_uil as pul

# supress warning messages like SSE4.1, AVX, etc.
os.environ['TF_CPP_MIN_LOG_LEVEL']='1'
#config = tf.ConfigProto()
#config.gpu_options.allow_growth = True
#session = tf.Session(config=config)

os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
#os.environ["CUDA_VISIBLE_DEVICES"]="0"
os.environ["TF_ENABLE_AUTO_MIXED_PRECISION"] = "1"
config = tf.ConfigProto()
#config.gpu_options.per_process_gpu_memory_fraction = 0.5
config.gpu_options.allow_growth = True
session = tf.Session(config=config)


import tensorflow as tf
import net_resnet_large_window
import resnet_v2
from keras.optimizers import Nadam
from keras.callbacks import EarlyStopping, ModelCheckpoint


def predict_classes(x):
#generate class prediction from the input samples
    y=x.argmax(axis=1)
    return y

#path2DataOfCity = '/data/hu/test/00005_21206_Mumbai'
path2DataOfCity = sys.argv[1]

#path2NetModel = '/data/hu/so2sat_CNN/RESNET20/models/S1_RESNET20_BS32_LR1e-4_IN32-32-7_PRO52A-R10-GLOBAL_2019_06_22.h5'
path2NetModel = sys.argv[2]


# 1. parameter setting
# feature selection
featSelection = [1,1,1,0,0,0,0,1,1,1,1]
# patch size
patchsize = 32
# patch shape
patch_shape = (32, 32, np.sum(featSelection))
# batch size
batch_size = 64


# 2. read data of a given city, feature extraction, patch cutting, and initial classification map tiff file
# read data path
dataPathTime = sen1cnn.getPathOfTime(path2DataOfCity)
# dataPathTif  = sen1cnn.getPath2Data(dataPathTime[0])
dataPathTif = dataPathTime[0] +'/mosaic.tif'


# initial classification map tiff file
LCZPaths = gp.initialLCZGrids(dataPathTif)
# get patch coordinate
coordCell = gp.getCoordLCZGrid(LCZPaths[0])
coordImage = gp.getImageCoordByXYCoord(coordCell,dataPathTif)
# read data and feature extraction
dataFeature,_,_  = sen1cnn.getDataNormMStd(dataPathTif, featSelection)
# cutting patches
dataPatches = gp.getPatch(dataFeature,coordImage,patchsize)


# 3. loading trained CNN and predict label
#model = net_resnet_large_window.build_model(patch_shape, nb_classes = 17 , start_ch = 16, depth = 4, inc_rate = 2, nb_skipped = 2, activation = 'relu')
model = resnet_v2.resnet_v2_s1(input_shape=patch_shape,depth=20, num_classes = 17)
timeStart = time.time()
model.load_weights(path2NetModel)
timeEnd = time.time()
#print('INFO:    TIME SPENT FOR LOADING TRAINED CNN MODEL IS: '+str(timeEnd-timeStart))
timeStart = time.time()
probPred = model.predict(dataPatches,batch_size = batch_size)
timeEnd = time.time()
print('INFO:    Time for infereencing '+str(timeEnd-timeStart))
#print(np.min(probPred))
#print(np.median(probPred))
#print(np.max(probPred))

labelPred = predict_classes(probPred)

# 4. save predicted probability and label
probPath = gp.saveProbabilityPrediction(probPred,LCZPaths[1])
labelPath = gp.saveLabelPrediction(labelPred,LCZPaths[0])

#print('9')
# 5. write ok file
try:
    #print('Try writing OK files')
    #os.system("printf '%s' \"0\" > OK.lcz_classification")
    with open('OK.lcz_classification', 'w') as out:
        out.write("0")
    #print('Write OK file finished')

except RuntimeError, e:
    print('ERROR:   Error in writing OK.lcz_classification.')
    print(e)

#print('10')






