=================
Outputs in detail
=================

.. _outputs_in_detail:

---------------------------------------------------
What the script is doing and what are the outputs ?
---------------------------------------------------

1. Sort dicom files according to series description
---------------------------------------------------

- The script copies the raw dicom files to ``${output_dir}/sourcedata/${subject}/ses-${session}``.
- Dicom files of for each series will be under a separate directory under 
the target directory, ``{series_number}_{series_description}``.
- The script has been designed to also work with a dicom directory, where all 
dicom files are dumped under a single directory. 

2. Dicom to BIDS using ``heudiconv``
------------------------------------

- The U24 specific heuristic config file ``phantom_check/data/heuristic.py`` 
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
-----------------------------------
- The script runs set of quality check pipelines to the data, and saves QC
outputs under ``${output_dir}/derivatives/``

- DWI preprocessing

- MRIQC

- Protocol check

- ``json_comparison_log.xlsx``: compare input dcm2niix sidecar jsons to
  json in tempalte BIDS data.
- ``json_comparison_log.txt``: same as above in a text format.
- ``series_count.csv``: check number of series against template BIDS data.
- ``volume_slice_number_comparison_log.csv``: check shape of nifti data 
  against template BIDS data.
- ``scan_order.csv``: check order of series acquisitions against template 
  BIDS data.
- ``bval_comparison_log.txt``: compare b-values and number of shells in DWI
  against template BIDS data.
- ``within_phantom_qc.txt``: compare consistency across series in a same
  session
- ``csa_headers.csv``: extract CSA header information for each series.
- ``json_check_image_orientation_in_anat.csv``
- ``json_check_image_orientation_in_dMRI_fMRI_and_distortionMaps.csv``
- ``json_check_shim_settings.csv``
- ``sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_dwi.png``
- ``sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_sbref.png``
- ``sub-BW00001_ses-202107221_acq-b0_dir-AP_run-1_dwi.png``
- ``sub-BW00001_ses-202107221_acq-b0_dir-AP_run-1_sbref.png``
- ``sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_dwi.png``
- ``sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_sbref.png``
- ``sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.png``
- ``sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.png``
- ``sub-BW00001_ses-202107221_rec-norm_run-1_T1w.png``
- ``sub-BW00001_ses-202107221_rec-norm_run-1_T2w.png``
- ``summary_b0.png``
- ``summary_dwi.png``
- ``summary_fmri.png``
