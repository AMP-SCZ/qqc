# phantom_check
Snippets used in the phantom QC


## Contents
1. B0 signal summary figure



## 1. B0 signal summary figure

This function plots average b0 signal in each volume for different scan runs.
It expects two AP b0 volumes and one PA dMRI volume, where the b0 volume will
be extracted. It will only include volumes with b-value > 50 (by default) in
the figure creation.

### Requirements
  - dcm2niix in $PATH
  - nibabel module in python


### How to run it

1. Unzip transferred phantom file
2. Summarize different b0 volumes using `phantom_figure.py`
  - Reqruies paths of directories that contain dicom files for each volumes.
  - This function runs `dcm2niix` saving outputs to a temporary file, which is
    then deleted after creating figure.
```
# to print help message
./phantom_figure.py -h

./phantom_figure.py  \
  --apb0dir1 phantom_dir/dMRI_b0_AP_20 \
  --apb0dir2 phantom_dir/dMRI_b0_AP_24 \
  --padmridir phantom_dir/dMRI_dir176_PA_22 \
  --out test.png

# Use different threshold for b0
./phantom_figure.py  \
  --apb0dir1 phantom_dir/dMRI_b0_AP_20 \
  --apb0dir2 phantom_dir/dMRI_b0_AP_24 \
  --padmridir phantom_dir/dMRI_dir176_PA_22 \
  --b0thr 100 \
  --out test.png
```
