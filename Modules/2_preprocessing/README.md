# Sentinel-1 Preprocessing
## Simple running
sentinel_1_processing.py runs a Sentinel-1 data preprocessing pipeline by calling graphic processing tool (gpt) of ESA SNAP toolbox. It delivers two data images. One has speckle, the other one had speckle reduction with LEE filter. The processing chains are as follows:
Apply orbit file, calibration, deburst, terrain correction, roi cropping, and mosaic (if necessary)
Apply orbit file, calibration, deburst, Lee filtering, terrain correction, roi cropping, and mosaic (if necessary)

This script basically calls the following functions:
python geocoding_core.py ../../data/Sentinel-1/00017_22007_Lagos templates/gpt_template_preprocessing_lee_KML_UTM.xml UN_city_list_rect_buff.kml
python geocoding_core.py ../../data/Sentinel-1/00017_22007_Lagos templates/gpt_template_preprocessing_unfilt_KML_UTM.xml  UN_city_list_rect_buff.kml 
python mosaic_core.py ../../data/Sentinel-1/00017_22007_Lagos gpt_template_preprocessing_lee_KML_UTM.xml UN_city_list_rect_buff.kml
python mosaic_core.py ../../data/Sentinel-1/00017_22007_Lagos gpt_template_preprocessing_unfilt_KML_UTM.xml UN_city_list_rect_buff.kml

## Issue of accessing orbit file
Currently (01.06.2021) Sentinel-1 orbit file is not automatically accessible via ESA SNAP. Details about this issue are extensively discussed in the [SNAP forum](https://forum.step.esa.int/t/orbit-file-timeout-march-2021/28621/178). In the discussion, one bypass solution is to download the orbit file from the [website](https://scihub.copernicus.eu/gnss/#/home) and put the files into the folder associated with the same month of the year in this path: /home/user/.snap/auxdata/Orbits/Sentinel-1/POEORB


# Sentine-2 Preprocessing
Resample sentinel-2 images from wgs84 to utm;
the utm projection is calculated from the ROI file in kml format
# Sample data
https://drive.google.com/drive/folders/1vs_eb3eBGzrk9m75gPEAOCtAzlRUv2BW?usp=sharing

# Usage
- set the pwd to the root folder of a city

`cd ./resampleData_projection_s2/00002_21228_Delhi`

- set ROI files which is used in `/datastore/DATA/classification/SEN2/2utmCode/LCZ/util/readROI2xyMinMax.py and readROI2UTM.py`

`export ROI='./resampleData_projection_s2/UN_city_list_rect_buff.kml'`

- set the path to the scripts: readROI2xyMinMax.py and readROI2UTM.py

`export P_UTIL='XXX/So2Sat-LCZ-Classification-Demo/Modules/Pre-processing'`

- call examples: absolutePath/project2utm_s2.sh folder4save

`XXX/So2Sat-LCZ-Classification-Demo/Modules/Pre-processing/project2utm_s2.sh /home/qiu/CodeSummary/img2map/resampleData_projection_s2/utmImage`
