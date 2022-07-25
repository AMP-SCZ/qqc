Steps in detail
=================

.. _steps_in_detail:

What the script is doing
------------------------

1. Sort dicom files according to series description
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The script copies the raw dicom files to ``${output_dir}/sourcedata/${subject}/ses-${session}``.
- Dicom files of for each series will be under a separate directory under 
the target directory, ``{series_number}_{series_description}``.
- The script has been designed to also work with a dicom directory, where all 
dicom files are dumped under a single directory. 

2. Dicom to BIDS using ``heudiconv``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The U24 specific heuristic config file ``qqc/data/heuristic.py`` 
is used. Output nifti files are saved under ``${output_dir}/rawdata/${subject}/ses-${session}``.
- List of modality directories are

- ``anat``: contains T1w and T2w, both normalized and non-normalized.

- ``dwi``: contains diffusion weighted images (DWI). 
  - PA acquisition (nifti, bval and bvec)
  - PA acquisition SBRef map
  - two AP b0 acquisitions (nifti, bval and bvec)
  - two AP SBRef maps

- ``fmap``: contains field maps.
  - AP and PA distortion maps before T1w scan
  - AP and PA distortion maps before first fMRI AP scan
  - AP and PA distortion maps before second fMRI AP scan

- ``func``: contains fMRI resting state scans.
  - First set of fMRI scans
      - AP and PA fMRI REST scans
      - SBRef volumes for each scans
  - Second set of fMRI scans
      - AP and PA fMRI REST scans
      - SBRef volumes for each scans

- ``ignore``: contains localizers and scout maps.
  - localizer
  - scout
  - alinged localizer

3. Quick quality check (QC) outputs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- The script runs set of quality check pipelines to the data, and saves QC
outputs under ``${output_dir}/derivatives/``

- DWI preprocessing

- MRIQC

- FMRIPREP

- Protocol check

   1. Comparison to the standard BIDS session given by user. :ref:`qqc_to_standard`
   2. Check consistency across the series in the same scan session. :ref:`qqc_same_session`
   3. Quick summary of signals in DWI and REST fMRI. :ref:`qqc_signals`
   4. Quick screen capture of all nifti files. :ref:`qqc_snapshot`

