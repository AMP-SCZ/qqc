Usage
=====

.. _usage:

dicom_to_dpacc_bids.py
----------------------

To process dicom files under ``/data/predict/kcho/flow_test/Pronet/PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/LA00006_MR_2021_07_22_1``,
compare them to ``/data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/ses-humanpilot``,
and save the outputs under ``/data/predict/kcho/flow_test/MRI_ROOT``, use the
command below:

.. code-block:: console

   $ dicom_to_dpacc_bids.py \
       --input_dir /data/predict/kcho/flow_test/Pronet/PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/LA00006_MR_2021_07_22_1 \
       --subject_name BW00001 \
       --session_name 202107221 \
       --output_dir /data/predict/kcho/flow_test/MRI_ROOT \
       --standard_dir /data/predict/phantom_human_pilot/rawdata/sub-ProNETUCLA/ses-humanpilot \


Command above creates structure below:

::

   /data/predict/kcho/flow_test/MRI_ROOT/
   ├── derivatives
   │   ├── dwipreproc
   │   │   └── sub-BW00001
   │   │       └── ses-202107221
   │   ├── mriqc
   │   │   ├── sub-BW00001
   │   │   │   └── ses-202107221
   │   │   │       ├── anat
   │   │   │       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.json
   │   │   │       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.json
   │   │   │       │   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T1w.json
   │   │   │       │   └── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.json
   │   │   │       └── func
   │   │   │           ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-1_bold.json
   │   │   │           ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-2_bold.json
   │   │   │           ├── sub-BW00001_ses-202107221_task-rest_dir-PA_run-1_bold.json
   │   │   │           └── sub-BW00001_ses-202107221_task-rest_dir-PA_run-2_bold.json
   │   │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.html
   │   │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.html
   │   │   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T1w.html
   │   │   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.html
   │   │   ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-1_bold.html
   │   │   ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-2_bold.html
   │   │   ├── sub-BW00001_ses-202107221_task-rest_dir-PA_run-1_bold.html
   │   │   └── sub-BW00001_ses-202107221_task-rest_dir-PA_run-2_bold.html
   │   └── quick_qc
   │       └── sub-BW00001
   │           └── ses-202107221
   │               ├── bval_comparison_log.txt
   │               ├── csa_headers.csv
   │               ├── json_check_image_orientation_in_anat.csv
   │               ├── json_check_image_orientation_in_dMRI_fMRI_and_distortionMaps.csv
   │               ├── json_check_shim_settings.csv
   │               ├── json_comparison_log.txt
   │               ├── scan_order.csv
   │               ├── series_count.csv
   │               ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_dwi.png
   │               ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_sbref.png
   │               ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-1_dwi.png
   │               ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-1_sbref.png
   │               ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_dwi.png
   │               ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_sbref.png
   │               ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.png
   │               ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.png
   │               ├── sub-BW00001_ses-202107221_rec-norm_run-1_T1w.png
   │               ├── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.png
   │               ├── summary_b0.png
   │               ├── summary_dwi.png
   │               ├── summary_fmri.png
   │               ├── volume_slice_number_comparison_log.csv
   │               └── within_phantom_qc.txt
   ├── rawdata
   │   └── sub-BW00001
   │       └── ses-202107221
   │           ├── anat
   │           ├── dwi
   │           ├── fmap
   │           ├── func
   │           └── ignore
   └── sourcedata
       └── BW00001
           └── ses-202107221
               ├── 01_Localizer
               ├── 02_AAHScout
               ├── 03_AAHScout_MPR_sag
               ├── 04_AAHScout_MPR_cor
               ├── 05_AAHScout_MPR_tra
               ├── 06_Localizer_aligned
               ├── 07_DistortionMap_AP
               ├── 08_DistortionMap_PA
               ├── 09_T1w_MPR
               ├── 10_T1w_MPR
               ├── 11_T2w_SPC
               ├── 12_T2w_SPC
               ├── 13_DistortionMap_AP
               ├── 14_DistortionMap_PA
               ├── 15_rfMRI_REST_AP_SBRef
               ├── 16_rfMRI_REST_AP
               ├── 17_rfMRI_REST_PA_SBRef
               ├── 18_rfMRI_REST_PA
               ├── 19_dMRI_b0_AP_SBRef
               ├── 20_dMRI_b0_AP
               ├── 21_dMRI_dir176_PA_SBRef
               ├── 22_dMRI_dir176_PA
               ├── 23_dMRI_b0_AP_SBRef
               ├── 24_dMRI_b0_AP
               ├── 25_DistortionMap_AP
               ├── 26_DistortionMap_PA
               ├── 27_rfMRI_REST_AP_SBRef
               ├── 28_rfMRI_REST_AP
               ├── 29_rfMRI_REST_PA_SBRef
               └── 30_rfMRI_REST_PA

Outputs in detail
-----------------

1. Sort dicom files according to series description
  - The script copies the raw dicom files to 
   ``${output_dir}/sourcedata/${subject}/ses-${session}``.
  - Dicom files of for each series will be under a separate directory under 
    the target directory, ``{series_number}_{series_description}``.
  - The script has been designed to also work with a dicom directory, where all 
    dicom files are dumped under a single directory. 

2. Dicom to BIDS using ``heudiconv``
  - The U24 specific heuristic config file ``phantom_check/data/heuristic.py`` 
    is used. Output nifti files are saved under 
   ``${output_dir}/rawdata/${subject}/ses-${session}``.
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
  - The script runs set of quality check pipelines to the data, and saves QC
    outputs under ``${output_dir}/derivatives/``
  - DWI preprocessing
  - MRIQC
  - Protocol check
    - ``json_comparison_log.xlsx``: compare input dcm2niix sidecar jsons to json
                                  in tempalte BIDS data.
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
