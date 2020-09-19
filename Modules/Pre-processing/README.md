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
