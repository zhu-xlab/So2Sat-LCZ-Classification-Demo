# LCZ map production with trained model
## Sentinel-1
Produce a classification map for 00017_22007_Lagos with a trained model and Sentinel-1 data
> python sen1InferenceResNet.py ../../data/Sentinel-1/00017_22007_Lagos model/S1_RESNET20_BS32_LR1e-4_IN32-32-7_PRO52A-R10-GLOBAL_2019_06_22.h5

## Sentinel-2
Produce a classification map for 00017_22007_Lagos with a trained model and multi-seasonal Sentinel-2 images
The softmax probability of each season and the fused LCZ labels are saved into geotiff files.
> CUDA_VISIBLE_DEVICES=0 python sen2InferenceResNet20.py '../../data/Sentinel-2/00017_22007_Lagos' 'model/S2_RESNET20_BS16_LR2e-4_IN32-32-10_PRO-52-0R12_2019-06-27T10:16:53+02:00.hdf5'

### Sentinel-2 sample data and trained model
- sampleData_So2Sat-LCZ-Classification-Demo https://drive.google.com/drive/u/0/folders/1ihzlEzswR03fJoV0bn_yL4qYf5rQKtgX

### Sentinel-2 Folder Structure
  ```
  Classification/
  │
  ├── sen2InferenceResNet20.py - main script to start predictions for a ROI with multi-seasonal images
  ├── resnet_v2.py - model
  ├── sen2_production_uil.py - read s2 data from tif files and prepare patches to feed into the network
  ├── production_uil.py - save the predictions into a geotiff file
  └──...
  ```
