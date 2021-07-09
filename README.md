# phantom_check
Snippets used in the phantom QC



#### Short example

```
./phantom_figure.py \
    --mode dmri \
    --dicom_dirs \
        ProNET_UCLA/dMRI_b0_AP_20 \
        ProNET_UCLA/dMRI_dir176_PA_22 \
        ProNET_UCLA/dMRI_b0_AP_24 \
    --names \
        apb0_1 pa_dmri apb0_2 \
    --b0thr 50 \
    --store_nifti \
    --out_image b0_summary.png

./dicom_header_comparison.py \
    --json_files \
        apb0_1/apb0_1.json \
        pa_dmri/pa_dmri.json \
        apb0_2/apb0_2.json \
    --save_excel json_summary.xlsx
```



## Contents

1. Signal summary figure
2. Compare json files



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
  - choose either `dmri` or  `general_4d`
  - providing `--mode dmri` option will make the script to
    -  look for `*.bval` files in the same directory with the prefix. 
    - use `--b0thr` to select specific volumes under a certain bvalue.
-  `--dicom_dirs`, `--nifti_prefixes` or `--nifti_dirs` 
  - use one of these three options to specify the data source.
  - you can provide more than one data point separated with a space
    - eg) `--nifti_prefixes dti_AP/dti_AP dti_PA/dti_PA'`
  - if `--dicom_dirs` is used
    - `dcm2niix` will be used to convert the dicoms into nifti in a temporary directory, which will be removed after loading the data from the nifti files.
    - use `--store_nifti` to save the `dcm2niix` outputs
      - names given to the `--names` will be used as the prefix in the `dcm2niix`, which will create directories under the current directory with the prefix.
- `--names`
  - a list of name to be used in the subtitle of each figures.
  - provide a short name for each of data source given in the same order as the data source.
  - if not given, the prefixes of the data sources will be used as the names.
- `--fig_num_in_row`
  - provide number of columns in the figure.
- `--wide_fig`
  - an option to be used when a horizontal figure would better fit the visualization purpose
- `--out_image`
  - name of the output summary image to be saved.



### Examples


```
# to print help message
./phantom_figure.py -h

# summaryize b0 from the dicom directories
./phantom_figure.py \
    --mode dmri \
    --dicom_dirs \
        ProNET_UCLA/dMRI_b0_AP_20 \
        ProNET_UCLA/dMRI_dir176_PA_22 \
        ProNET_UCLA/dMRI_b0_AP_24 \
    --names \
        apb0_1 pa_dmri apb0_2 \
    --store_nifti \
    --out_image new_test_dmri.png


# summaryize non-dMRI data
./phantom_figure.py \
    --mode fMRI \
    --dicom_dirs \
        ProNET_UCLA/fMRI_AP_1 \
        ProNET_UCLA/fMRI_AP_2 \
        ProNET_UCLA/fMRI_PA_1 \
    --names \
       fMRI_AP_1 fMRI_AP_2 fMRI_PA_1 \
    --out_image new_test_fmri.png


# run summary on nifti directories
./phantom_figure.py \
    --mode dmri \
    --nifti_dirs apb0_1 pa_dmri apb0_2 \
    --names apb0_1 pa_dmri apb0_2 \
    --b0thr 5000 \
    --out_image new_test_nifti_dir_thr5000.png

```



## 2. Compare json files

dcm2niix creates a bids side car in a json file. `dicom_header_comparison.py` is used compare command and unique values in each items of the json file.



### How to run it

1. Unzip transferred phantom file
2. Summarize the different between difference scans using `dicom_header_comparison.py`



#### Options in `dicom_header_comparison.py`

-  `--dicom_dirs`, `--json_files` or `--multi_file_dir` 
  - use one of these three options to specify the data source.
  - you can provide more than one data point separated with a space
    - eg) `--json_files dti_AP/dti_AP dti_PA/dti_PA'`
  - if `--dicom_dirs` is used
    - `dcm2niix` will be used to convert the dicoms into nifti in a temporary directory, which will be removed after loading the data from the nifti files.
    - use `--store_nifti` to save the `dcm2niix` outputs
      - names given to the `--names` will be used as the prefix in the `dcm2niix`, which will create directories under the current directory with the prefix.
- `--print_diff`: print the differences between each json source compared to each other, on screen.
- `--print_shared`: print common items between each json source compared to each other, on screen.
- `--save_excel`: takes a path of excel file path to save the differences.




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

