

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

- define/setup models in modelS_hse.py: `CUDA_VISIBLE_DEVICES=0 python sen2InferenceResNet20.py 'sampleData_So2Sat-LCZ-Classification-Demo/00017_22007_Lagos' 'sampleData_So2Sat-LCZ-Classification-Demo/S2_RESNET20_BS16_LR2e-4_IN32-32-10_PRO-52-0R12_2019-06-27T10:16:53+02:00.hdf5'`
