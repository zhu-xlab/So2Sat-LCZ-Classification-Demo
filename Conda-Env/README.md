'''
26.08.2020. by Jingliang Hu
'''

# python library for Sentinel-1 data download
1. Create a new conda environment by command "conda create --name sipeo_so2sat_demo python"
2. Start the env by command "source activate sipeo_so2sat_demo"
3. Install gdal by command "conda install gdal"; Start python and use "from osgeo import ogr,osr,gdal" to check whether the installation is success or not
4. Install shapely by command "conda install shapely"; Installation check "from shapely.wkt import loads"
5. Install sentinelsat by command "pip install sentinelsat"; Installation check "import sentinelsat"
6. Install pandas by command "conda install pandas"; Installation check "import pandas as pd"





# Recreate an identical conda env with .yml file
1. activate original env: 	source activate sipeo_so2sat_demo
2. generate .yml file: 		conda env export > sipeo_so2sat_demo_env.yml


