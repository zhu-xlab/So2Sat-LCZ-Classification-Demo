# So2Sat LCZ Classification Demo
## Introduction
This repository provides a demo that produces local climate zone classification maps using Sentinel-1 and Sentinel-2 data. This is a part of an European Research Council (ERC) starting grand project "So2Sat" [So2Sat page](http://www.so2sat.eu/).
![vancouver lcz map](https://github.com/zhu-xlab/So2Sat-LCZ-Classification-Demo/blob/master/data/MAP/Sentinel-2/lcz_vancouver.png)
Figure: local climate zone map of the city Vancouver

## Environment setting
This demo has been tested in a conda environment. The following steps create an identical conda environment as ours.
### Step 1: Install anaconda
[Please refer to anaconda documentation](https://docs.anaconda.com/anaconda/install/)
### Step 2: Create an identical conda env as ours
1. More to directory "Conda-Env"
2. Create env from yml file. One can change the name of the env by changing the first line of the file sipeo_so2sat_demo_env.yml
> conda env create -f sipeo_so2sat_demo_env.yml
3. Check the env
> conda env list

## Exemplary data
Please download the exemplary data [here](ftp://ftp.lrz.de/transfer/temporary_data_storage/So2Sat_LCZ_Classification_Demo/), and place the directory "data" at the top level.

## Code organization
The workflow of this demo consists of data downloading, data preprocessing, classification with trained model, and decision fusion. These four modules are in the directory "Modules"

