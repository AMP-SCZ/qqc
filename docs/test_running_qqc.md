# Test running QQC


## Contents
1. Requirements
2. Example commands



## 1. Requirements

- `qqc` in your `PYTHONPATH`
- `dcm2niix` in your `PATH`
- If ```--standard_dir``` is not specified, the program will search for a standard template in the configuration file. 


## 2. Example commands
- Example of adding `qqc` to `PYTHONPATH`: ```export PYTHONPATH=/data/predict1/home/kcho/software/qqc:$PYTHONPATH```
- Check for ```dcm2niix``` with ```which dcm2niix```

```sh
/data/pnl/kcho/anaconda3/bin/python \
    /data/predict1/home/kcho/software/qqc/scripts/dicom_to_dpacc_bids.py \
           -i /data/predict1/data_from_nda/Pronet/PHOENIX/PROTECTED/PronetXX/raw/XX02821/mri/XX02821_MR_2023_01_26_1.zip \
           -s XX02821 \
           -ss 2023_01_26_1 \
           -o ~/test_root --email_report \
           --standard_dir /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-XX02398/ses-20230301
```
