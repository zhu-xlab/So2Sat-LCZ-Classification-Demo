# Sentinel-1 Preprocessing
## How to run
### Step 1. Set path to ESA SNAP GPT
One needs to install [ESA SNAP toolbox](https://step.esa.int/main/download/snap-download/) and set the directory of ESA SNAP GPT (e.g. ~/snap/bin/gpt) at line 10 of "sentinel_1_processing.py"
```
os.environ['gpt'] = '~/snap/bin/gpt'
```
### Step 2. Manually copy orbit profile to SNAP directory
Automatic downloading of orbit profiles might be an issue in SNAP. Therefore, we have included the orbit data for city Lagos in the sample data. 
```
mkdir ~/.snap/auxdata/Orbits/Sentinel-1/POEORB/S1A/2021/05
cp data/Sentinel-1/00017_22007_Lagos/orbit_profile/S1A_OPER_AUX_POEORB_OPOD_20210528T121723_V20210507T225942_20210509T005942.EOF ~/.snap/auxdata/Orbits/Sentinel-1/POEORB/S1A/2021/05
```
One can also download orbit profiles [here](https://scihub.copernicus.eu/gnss/#/home) when necessary.
### Step 3. Run the processing script
```bash
python sentinel_1_processing.py
```
```bash
#sentinel_1_processing.py basically calls the following functions:
python geocoding_core.py ../../data/Sentinel-1/00017_22007_Lagos templates/gpt_template_preprocessing_lee_KML_UTM.xml UN_city_list_rect_buff.kml
python geocoding_core.py ../../data/Sentinel-1/00017_22007_Lagos templates/gpt_template_preprocessing_unfilt_KML_UTM.xml  UN_city_list_rect_buff.kml 
python mosaic_core.py ../../data/Sentinel-1/00017_22007_Lagos gpt_template_preprocessing_lee_KML_UTM.xml UN_city_list_rect_buff.kml
python mosaic_core.py ../../data/Sentinel-1/00017_22007_Lagos gpt_template_preprocessing_unfilt_KML_UTM.xml UN_city_list_rect_buff.kml
```
## Processing pipeline
It runs a Sentinel-1 data preprocessing pipeline by calling graphic processing tool (gpt) of ESA SNAP toolbox. It delivers two data images. One has speckle, the other one had speckle reduction with LEE filter. The processing chains are as follows:

"Apply orbit file, calibration, deburst, terrain correction, roi cropping, and mosaic (if necessary)"

"Apply orbit file, calibration, deburst, Lee filtering, terrain correction, roi cropping, and mosaic (if necessary)"

Details about the processing can be find in the following paper. Figure 4 in it provides a visualization.

> Hu, Jingliang, Pedram Ghamisi, and Xiao Xiang Zhu. "Feature extraction and selection of sentinel-1 dual-pol data for global-scale local climate zone classification." ISPRS International Journal of Geo-Information 7.9 (2018): 379.


## Requirement and possible issue
Before running, one needs to install [ESA SNAP toolbox](https://step.esa.int/main/download/snap-download/) and set the directory to ESA SNAP GPT (e.g. ~/snap/bin/gpt) at line 10 of "sentinel_1_processing.py"

Currently (01.06.2021) Sentinel-1 orbit file is not automatically accessible via ESA SNAP. Details about this issue are extensively discussed in the [SNAP forum](https://forum.step.esa.int/t/orbit-file-timeout-march-2021/28621/178). In the discussion, one bypass solution is to download the orbit file from the [website](https://scihub.copernicus.eu/gnss/#/home) and put the files into the folder associated with the same month of the year in this path: /home/user/.snap/auxdata/Orbits/Sentinel-1/POEORB

The pre-processing might has an issue accessing DEM for terrain correction. Two tricks are helpful for us. One is installing the latest SNAP toolbox. The other is changing SRTM 3Sec to SRTM 1Sec HGT or other options.

# Sentinel-2 Preprocessing
The Sentinel-2 images are downloaded as cloud free images aggregated over three months. Details are in the following paper.
> Schmitt, Michael, et al. "Aggregating cloud-free Sentinel-2 images with Google earth engine." PIA19: Photogrammetric Image Analysis (2019): 145-152.

Sentinel-2 images are then reprojected to the same WGS84/UTM zone as the Sentinel-1 data.


<!---  COMMENT OUT
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
--->
