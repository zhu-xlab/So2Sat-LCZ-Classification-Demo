# set up environment
keras:		conda install -c conda-forge keras

# produce a classification map for city 00331_204371_Munich with trained model
python global_production.py ../../data/Sentinel-1/00331_204371_Munich model/S1_RESNET20_BS32_LR1e-4_IN32-32-7_PRO52A-R10-GLOBAL_2019_06_22.h5
