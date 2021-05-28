# Data download
## Sentinel-1
The script "sentinel_1_download.py" downloads sentinel-1 level-1 SLC IW (VV-VH) product automatically, based on the python API sentinelsat, from sentinel data hub. 

If one runs "sentinel_1_download.py" directly, it downloads data for city Lagos and Chengdu as examples. Current script loads ROIs from "../../data/ROI/UN_city_list_rect_buff.kml". The downloaded data will be saved in "../../data/Sentinel-1/". If the required data tile is not online, this script retrieves the data and attempts downloading again 20 minutes later.
