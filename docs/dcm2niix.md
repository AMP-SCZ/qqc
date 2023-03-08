# dcm2niix

QQC uses `heudiconv` to convert the raw dicom files to nifti files following the BIDS file structure. Since `heudiconv` calls `dcm2niix` in the conversion process, QQC users need to have `dcm2niix` in their shell environment.


### Test if you have `dcm2niix` available already in your shell

```sh
which dcm2niix
```

If it returns a path of `dcm2niix`, your system has `dcm2niix` configured.


## Setting up dcm2niix

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
/data/predict1/home/kcho/software/dcm2niix_1d4413e_20230121/build/bin/dcm2niix
```

If you want to use the `dcm2niix` above, add the following to your `~/.bashrc` and `source ~/.bashrc`
```sh
export PATH=/data/predict1/home/kcho/software/dcm2niix_1d4413e_20230121/build/bin:${PATH}
```
