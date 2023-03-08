# Setting up dcm2niix

QQC uses `heudiconv` in converting dicom files to BIDS structured nifti files. Since `heudiconv` calls `dcm2niix` in the conversion process,
QQC users need to have `dcm2niix` in their shell environment.

`dcm2niix` can be downloaded from here https://github.com/rordenlab/dcm2niix/tree/development

Once it is downloaded and compiled, add the `dcm2niix`'s bin directory to the `PATH`.

```sh
# Add the following line to your ~/.bashrc 
export PATH=/path/to/dcm2niix/root:${PATH}

# save
# then source ~/.bashrc before runnign QQC
```


### The current version the dcm2niix that AMP-SCZ MRI team is using is under here
```sh
/data/predict1/home/kcho
```
