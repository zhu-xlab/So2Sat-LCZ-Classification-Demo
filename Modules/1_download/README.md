# Data download
## Sentinel-1
The script "sentinel_1_download.py" downloads sentinel-1 level-1 SLC IW (VV-VH) product automatically from the sentinel data hub, based on the python API sentinelsat,

## Example
Download the data of city Lagos as an example
> python sentinel_1_download.py

From line 23 to 51, one can set the parameters
```
###############################################################################
# Parameter setting
# An ROI example. A kml file contains ROI of 1692 cities whose population are larger than 300,000 in 2015
cityrois = '../../data/ROI/UN_city_list_rect_buff.kml'

# example city Lagos (One of the 1692 cities in the kml file). 
# [population ranking]_[city ID]_[city name]
cityname = ["00017_22007_Lagos"]

# Time period
# Search data in three time periods: 
startDate = ["20210501"]
endDate   = ["20210510"]

# directory of data to be saved
outdir = '../../data/Sentinel-1/'
###############################################################################
```

Current script loads ROIs from 
> ../../data/ROI/UN_city_list_rect_buff.kml

Downloaded data will be stored in the following directory:
> ../../data/Sentinel-1/

If the required data tile is not online, this script retrieves the data and attempts downloading again 20 minutes later.
