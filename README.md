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

# summaryize b0 from the dicom directories
./phantom_figure.py \
    --mode dmri_b0 \
    --dicom_dirs \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
    --names \
        apb0_1 pa_dmri apb0_2 \
    --out_image new_test.png


# allows more than three dicom inputs
./phantom_figure.py \
    --mode dmri_b0 \
    --dicom_dirs \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
    --names \
        apb0_1 pa_dmri apb0_2 dup \
    --out_image new_test_dup.png


# store outputs from the dcm2niix
./phantom_figure.py \
    --mode dmri_b0 \
    --dicom_dirs \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
    --names \
        apb0_1 pa_dmri apb0_2 \
    --store_nifti \
    --out_image new_test_dup.png


# run summary on nifti directories
./phantom_figure.py \
    --mode dmri_b0 \
    --nifti_dirs apb0_1 pa_dmri apb0_2 \
    --names apb0_1 pa_dmri apb0_2 \
    --out_image new_test_nifti_dir.png


# use different threshold when summarizing the b0
./phantom_figure.py \
    --mode dmri_b0 \
    --nifti_dirs apb0_1 pa_dmri apb0_2 \
    --names apb0_1 pa_dmri apb0_2 \
    --b0thr 5000 \
    --out_image new_test_nifti_dir_thr5000.png
```
