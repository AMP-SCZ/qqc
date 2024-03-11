# dcm2niix

QQC uses `heudiconv` to convert the raw dicom files to nifti files following the BIDS file structure. Since `heudiconv` calls `dcm2niix` in the conversion process, QQC users need to have `dcm2niix` in their shell environment.




## Contents

1. Test if you have `dcm2niix` available in your shell
2. Setting up `dcm2niix` in PNL
3. Setting up `dcm2niix` outside PNL
4. Using `dcm2niix`



## Test if you have `dcm2niix` available already in your shell

```sh
which dcm2niix
```
If it returns a path of `dcm2niix`, your system has `dcm2niix` configured.


## Setting up `dcm2niix` in PNL

### The current version the dcm2niix that AMP-SCZ MRI team is using is under here

```sh
/data/predict1/home/kcho/software/dcm2niix_1d4413e_20230121/build/bin/dcm2niix
```

If you want to use the `dcm2niix` above, add the following to your `~/.bashrc` and `source ~/.bashrc`
```sh
export PATH=/data/predict1/home/kcho/software/dcm2niix_1d4413e_20230121/build/bin:${PATH}

# then see if the command below returns the correct path of the dcm2niix
which dcm2niix
```

## Setting up `dcm2niix` outside PNL

`dcm2niix` can be downloaded from here https://github.com/rordenlab/dcm2niix/tree/development

Once it is downloaded and compiled, add the `dcm2niix`'s bin directory to the `PATH`.

```sh
# Add the following line to your ~/.bashrc 
export PATH=/path/to/dcm2niix/root:${PATH}

# then see if the command below returns the correct path of the dcm2niix
which dcm2niix
```


## Using `dcm2niix`

Read through available options.

```sh
dcm2niix -h
```

For most of conversion jobs, you can use the following command

```sh
dcm2niix -o /output/dir /dicom/dir
```


