# phantom_check
Snippets used in the phantom QC


## Contents
1. Signal summary figure
2. Compare json files



## Quick summary

```
./phantom_figure.py \
    --mode dmri_b0 \
    --dicom_dirs \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_20 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_dir176_PA_22 \
        /data/predict/phantom_data/ProNET_UCLA/dMRI_b0_AP_24 \
    --names \
        apb0_1 pa_dmri apb0_2 \
    --store_nifti \
    --out_image b0_summary.png

./dicom_header_comparison.py \
    --json_files \
        apb0_1/apb0_1.json \
        pa_dmri/pa_dmri.json \
        apb0_2/apb0_2.json \
    --save_excel json_summary.xlsx
```


## 1. Signal summary figure

This function plots average signal in each volume for different scan runs.
It expects a list of data sources, where the average signal for all voxels will
be used to create a figure. Extra options are available for b0 signal extraction
for dMRI scans.

### Requirements
  - dcm2niix in $PATH
  - nibabel module in python


### How to run it

1. Unzip transferred phantom file
2. Summarize different 4d images using `phantom_figure.py`



#### Options in `phantom_figure.py`

- `--mode`
  - choose either `dmri_b0` or  `general_4d`
  - 

  - Reqruies paths of directories that contain dicom files for each volumes.
  - This function runs `dcm2niix` saving outputs to a temporary file, which is
    then deleted after creating figure.
  - use one of `--dicom_dirs`, `--nifti_prefixes` or `--nifti_dirs` to specify
    your input to `phantom_figure.py`
  - If it's dMRI data, which also requires to load bvalue text files, use
    `--mode dmri_b0`, otherwise use `--mode fMRI`. 
  - Provide how you would call each input source to `--names`. The number of 
    names must match the number of input sources.
    eg) `--names dmri_b0_ap dmri_b0_pa`
  - `--out_image` option should specify the name of the output figure.
    eg) `--out_image diffusion_b0_summary.png`



### Examples


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

# summaryize non-dMRI data
./phantom_figure.py \
    --mode fMRI \
    --dicom_dirs \
        /data/predict/phantom_data/ProNET_UCLA/fMRI_AP_1 \
        /data/predict/phantom_data/ProNET_UCLA/fMRI_AP_2 \
        /data/predict/phantom_data/ProNET_UCLA/fMRI_PA_1 \
    --names \
       fMRI_AP_1 fMRI_AP_2 fMRI_PA_1 \
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



## 2. Compare json files

dcm2niix creates a bids side car in a json file. `dicom_header_comparison.py`
is used compare command and unique values in each items of the json file.


### How to run it

```
# to print help message
./dicom_header_comparison.py -h

# summaryize three json files and print the comparison table
./dicom_header_comparison.py \
    --json_files \
        dMRI_b0_AP_20.json \
        dMRI_dir176_PA_22.json \
        dMRI_b0_AP_24.json \
    --print_diff \
    --print_shared


# summaryize b0 from the dicom directories
./dicom_header_comparison.py \
    --json_files \
        dMRI_b0_AP_20.json \
        dMRI_dir176_PA_22.json \
        dMRI_b0_AP_24.json \
    --save_excel json_summary.xlsx
```

