# Standard dataset used in QQC

The new dataset is compared to another dataset in the QQC process. 


## What is a good template dataset?

The following list shows criteria for a good standard dataset to compare the new data.

1. Has all the required series. _01_scan_order.csv should have no fails_.

2. No duplication of any series. _02_series_count.csv should have no extras_.

3. All series taken with the correct protocol. _03_volume_slice_number_comparison_log.csv should have no fails_.

4. BIDS structured output with BIDS sidecar json files. _There should be one JSON per nifti file_.

5. Scanned near the beginning of the study. _This is a preference_.

Each AMP-SCZ site should have a standard dataset, so any changes in the new scan can be detected by QQC. We will use "Standard template" to describe
the standard dataset.


## How to specify which standard template to use
There are two ways to specify the standard template with QQC.

### 1. Specify the location of the standard template when you exeucte `dicom_to_dpacc_bids.py`

eg)
```sh
dicom_to_dpacc_bids.py \
    -i input_data.zip \
    -s AB00001 -ss 20231225 -o /data/predict1/data_from_nda/MRI_ROOT \
    --standard_dir /data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-LS/ses-202211071
```


### 2. Specify the location of the standard template for each site in a configuration file.

If `--standard_dir` is not specified from the shell command, QQC will look for the standard template in a configuration file. QQC will use the site code in the subject id (`-s`) to get the site code (first two letters) and match its standard template. The configuration file is structured in a way that different logics can be used to select different standard templates for a site eg) for an updated software version. The location of the configuration in the current PNL system is: `/data/predict1/data_from_nda/MRI_ROOT/standard_templates.cfg`.

Please make sure the permission of the configuration file is readable by the group, so others can read this configuration file when executing QQC.

eg)
```cfg
[First Scan]
AB = /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-AB04513/ses-202208311
DE = /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-DE21922/ses-202209021
FG = /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-FG00697/ses-202208151

[XA30 template]
ZZ = /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ZZ97666/ses-202302011
IS = /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ZZ97666/ses-202212202

[XA30 template enhanced]
ZZ = /data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-ZZ/ses-202211071
IS = /data/predict1/data_from_nda/MRI_ROOT/rawdata/sub-ZZ97666/ses-202212202

[XA30 template interoperability]
ZZ = /data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-ZZ71238/ses-202301261

[GE template]
a = /data/predict1/home/kcho/MRI_site_cert/qqc_output/rawdata/sub-HH/ses-202211031

[GE diffusion]
PA bval = /data/predict1/data_from_nda/MRI_ROOT/codes/GE_bval_bvec/dMRI_dir126_PA.bval
```

A standard template location is assigned to a site. Also by providing the location of standard template under the specific section,
eg) `First Scan`, the QQC can load different standard template to use depending on different situations.


