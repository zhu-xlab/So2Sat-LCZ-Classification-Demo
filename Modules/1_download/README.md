# Data download
## Sentinel-1
The script "sentinel_1_download.py" downloads sentinel-1 level-1 SLC IW (VV-VH) product automatically from the sentinel data hub, based on the python API sentinelsat,

## Example
Download the data of city as an example
> python sentinel_1_download.py

If one runs "sentinel_1_download.py" directly, it downloads data for city Lagos as example. Current script loads ROIs from "../../data/ROI/UN_city_list_rect_buff.kml". The downloaded data will be saved in "../../data/Sentinel-1/". If the required data tile is not online, this script retrieves the data and attempts downloading again 20 minutes later.

Downloaded data will be stored in the following directory:
> ../../data/Sentinel-1/
