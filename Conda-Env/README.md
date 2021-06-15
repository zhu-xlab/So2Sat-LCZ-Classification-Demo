# Environment setting
This demo has been tested in a conda environment. The following steps create an identical conda environment as ours.
## Step 1: Install anaconda
[Please refer to anaconda documentation](https://docs.anaconda.com/anaconda/install/)
## Step 2: Create an identical conda env as ours
1. More to directory "Conda-Env"
2. Create env from yml file. One can change the name of the env by changing the first line of the file sipeo_so2sat_demo_env.yml
> conda env create -f sipeo_so2sat_demo_env.yml
3. Check the env
> conda env list


### Extra (Not important)
python library for Sentinel-1 data download
1. Create a new conda environment 
> conda create --name sipeo_so2sat_demo python
2. Start the env
> source activate sipeo_so2sat_demo
3. Install gdal and check
> conda install gdal 
>
> python
> 
> from osgeo import ogr,osr,gdal
4. Install shapely and check
> conda install shapely
> 
> python
> 
> from shapely.wkt import loads"
5. Install sentinelsat and check
> pip install sentinelsat
> 
> python
> 
> import sentinelsat
6. Install pandas and check
> conda install pandas
> 
> python
> 
> import pandas as pd

