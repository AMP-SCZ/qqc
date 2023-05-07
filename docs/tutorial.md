Tutorial
--------

## Contents

1. Clone the repository
2. Run a function
2. Run a commandline executable code


## Clone the repository

1. Clone the QQC code from github

```sh
cd ~
git clone https://github.com/AMP-SCZ/qqc
cd qqc
```

2. Check your branch

`pnldev` branch should have the most recent updates.

```sh
git branch
```


## Run a function

1. Add the local path of the qqc to `PYTHONPATH` variable

This line lets the python interpreter to look for python modules under `~/qqc`
when importing libraries.

```sh
cd ~/qqc  # use your qqc path
export PYTHONPATH=${PWD}:${PYTHONPATH}
```


2. Go into python interpreter

```sh
ipython  # or python
```


3. Import a function from `qqc`

```py
from qqc.dicom_files import get_dicom_files_walk
from pathlib import Path

data_root = Path('/data/predict1/data_from_nda/MRI_ROOT')
dicom_location = data_root / 'sourcedata' / 'AB12345' / 'ses-202303141'
df = get_dicom_files_walk(dicom_location)
print(df)
```



## Run a commandline executable code

1. Add the local path of the qqc to `PYTHONPATH` variable

This line lets the python interpreter to look for python modules under `~/qqc`
when importing libraries.

```sh
cd ~/qqc  # use your qqc path
export PYTHONPATH=${PWD}:${PYTHONPATH}
```


2. Run a commandline executable code

```sh
cd scripts
mri_zip_file=/data/to/zip/data.zip
subject=AB12345
session=202303141
MRI_ROOT=/data/predict1/data_from_nda/MRI_ROOT_test
python /Users/kc244/qqc/scripts/dicom_to_dpacc_bids.py \
    -i ${mri_zip_file} -s ${subject} -ss ${session} -o ${MRI_ROOT} \
    --quick_scan \
    --email_report \
    --config /data/predict1/data_from_nda/MRI_ROOT/standard_templates.cfg \
    --force_heudiconv \
    --dwipreproc --mriqc --fmriprep \
    --additional_recipients \
        'kc244@research.partners.org'
```
