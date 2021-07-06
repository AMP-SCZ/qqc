# phantom_check
Snippets used in the phantom QC


- Requirements
  - nibabel


- How to run it from the shell
```
# to print help message
./phantom_figure.py -h

./phantom_figure.py  \
  --apb0dir1 phantom_dir/dMRI_b0_AP_20 \
  --apb0dir2 phantom_dir/dMRI_b0_AP_24 \
  --padmridir phantom_dir/dMRI_dir176_PA_22 \
  --out test.png
```

