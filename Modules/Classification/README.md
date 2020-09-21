# Sentinel-1 part
# produce a classification map with trained model for Sentinel-1 data
global_production.py ../../data/Sentinel-1/00331_204371_Munich model/S1_RESNET20_BS32_LR1e-4_IN32-32-7_PRO52A-R10-GLOBAL_2019_06_22.h5

# set up environment
keras:          conda install -c conda-forge keras

# produce a classification map for city 00331_204371_Munich with trained model
python global_production.py ../../data/Sentinel-1/00331_204371_Munich model/S1_RESNET20_BS32_LR1e-4_IN32-32-7_PRO52A-R10-GLOBAL_2019_06_22.h5




# Sentinel-2 part
LCZ classification from sentinel-2 images; multi-seasonal predictions are fused into one.
The softmax probability of each season and the fused LCZ labels are saved into geotiff files.

# Sample data and trained model
- sampleData_So2Sat-LCZ-Classification-Demo https://drive.google.com/drive/u/0/folders/1ihzlEzswR03fJoV0bn_yL4qYf5rQKtgX

# Folder Structure
  ```
  Classification/
  │
  ├── sen2InferenceResNet20.py - main script to start predictions for a ROI with multi-seasonal images
  ├── resnet_v2.py - model
  ├── sen2_production_uil.py - read s2 data from tif files and prepare patches to feed into the network
  ├── production_uil.py - save the predictions into a geotiff file
  └──...
  ```

# Usage

- `CUDA_VISIBLE_DEVICES=0 python sen2InferenceResNet20.py 'sampleData_So2Sat-LCZ-Classification-Demo/00017_22007_Lagos' 'sampleData_So2Sat-LCZ-Classification-Demo/S2_RESNET20_BS16_LR2e-4_IN32-32-10_PRO-52-0R12_2019-06-27T10:16:53+02:00.hdf5'`







