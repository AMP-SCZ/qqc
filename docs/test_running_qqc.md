# Test running QQC


## Contents
1. Requirements
2. Example commands



## 1. Requirements

- `qqc` in your `PYTHONPATH`
- `dcm2niix` in your `PATH`


## 2. Example command

```sh
/data/pnl/kcho/anaconda3/bin/python \
    /data/predict1/home/kcho/software/qqc/scripts/dicom_to_dpacc_bids.py \
           -i /data/predict1/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetXX/raw/XX02821/mri/XX02821_MR_2023_01_26_1.zip \
           -s XX02821 \
           -ss 2023_01_26_1 \
           -o ~/test_root --email_report \
           --standard_dir /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-XX02398/ses-20230301
```
