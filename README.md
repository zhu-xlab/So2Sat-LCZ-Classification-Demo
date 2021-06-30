# So2Sat LCZ Classification Demo
## Introduction
This repository provides a demo that produces local climate zone classification maps using Sentinel-1 and Sentinel-2 data with the model pre-trained by the So2Sat project team. This is a part of an European Research Council (ERC) starting grand project "So2Sat" [So2Sat page](http://www.so2sat.eu/).
![vancouver lcz map](https://github.com/zhu-xlab/So2Sat-LCZ-Classification-Demo/blob/master/data/MAP/lcz_vancouver.png)

Figure: local climate zone map of the city Vancouver

## Environment setting
This demo has been tested in a conda environment. The following steps create an identical conda environment as ours.
### Step 1: Install anaconda
[Please refer to anaconda documentation](https://docs.anaconda.com/anaconda/install/)
### Step 2: Create an identical conda env as ours
```bash
cd Conda-Env
conda env create -f sipeo_so2sat_demo_env.yml #Create env from yml file
conda env list #Check the env
```

## Exemplary data
Please download the exemplary data in the following link, and place the directory "data" at the top level.
> ftp://ftp.lrz.de/transfer/temporary_data_storage/So2Sat_LCZ_Classification_Demo/

## LCZ mapping workflow
This part shows the LCZ mapping workflow with the example of city Lagos.
### 1. LCZ mapping with Sentinel-1
Brower to Modules/3_classification
> cd Modules/3_classification

Produce a classification map for 00017_22007_Lagos with a trained model and Sentinel-1 data
> python sen1InferenceResNet.py ../../data/Sentinel-1/00017_22007_Lagos model/S1_RESNET20_BS32_LR1e-4_IN32-32-7_PRO52A-R10-GLOBAL_2019_06_22.h5

Produced classification map
> ../../data/Sentinel-1/00017_22007_Lagos/LCZ_ResNet/[TIME]/LCZLabel.tif

### 2. LCZ mapping with Sentinel-2
Brower to Modules/3_classification
> cd Modules/3_classification

Produce a classification map for 00017_22007_Lagos with a trained model and multi-seasonal Sentinel-2 images
The softmax probability of each season and the fused LCZ labels are saved into geotiff files.
> CUDA_VISIBLE_DEVICES=0 python sen2InferenceResNet20.py '../../data/Sentinel-2/00017_22007_Lagos' 'model/S2_RESNET20_BS16_LR2e-4_IN32-32-10_PRO-52-0R12_2019-06-27T10:16:53+02:00.hdf5'

Produced classification map
> ../../data/Sentinel-2/00017_22007_Lagos/LCZ_ResNet20/00017_22007_Lagos_lab.tiff

### 3. LCZ mapping by fusing Sentinel-1 and Sentinel-2
Brower to Modules/4_decision_fusion/
> cd Modules/4_decision_fusion/

Decision fusion:
> python sen1sen2Fusion.py ../../data/Sentinel-1/00017_22007_Lagos ../../data/Sentinel-2/00017_22007_Lagos

Produced fusion map:
> ../../data/MAP/00017_22007_Lagos/LCZ_Fusion/[TIME]/s1_s2_fusion.tif

### 4. Extra: data downloading and processing
Contents for data downloading can be found:
> Modules/1_download

Contents for data preprocessing can be found:
> Modules/2_preprocessing
