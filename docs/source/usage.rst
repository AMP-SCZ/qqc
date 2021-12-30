=====
Usage
=====

.. _usage:

----------------------
dicom_to_dpacc_bids.py
----------------------

To process dicom files under ``PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/BW00001_MR_2021_07_22_1``,
compare them to ``rawdata/sub-ProNETUCLA/ses-humanpilot``, and save the
outputs under ``MRI_ROOT``, use the command below:

.. code-block:: console

   $ dicom_to_dpacc_bids.py \
       --input_dir PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/BW00001_MR_2021_07_22_1 \
       --subject_name BW00001 \
       --session_name 202107221 \
       --output_dir MRI_ROOT \
       --standard_dir rawdata/sub-ProNETUCLA/ses-humanpilot \


1. ``--input_dir`` can virtually take any form of structure as long as there are
   dicom files under the directory.

2. For ``--subject_name``, use the subject ID. ``sub-`` prefix will be attached
   in front of the given subject name. eg) ``--subject_name BW00001``

3. For ``--session_name``, use the date and unique label number without any
   spaces, `-`, or `_`. eg) ``--session_name 202107221``

4. ``--output_dir`` is the root directory of the output. This path is where 
   ``sourcedata``, ``rawdata`` and ``derivatives`` directories will be created.

5. ``--standard_dir`` is the root of **BIDS session** that you would like to
   compare the protocols of the ``--input_dir``.


Available options
-----------------

1. Run extra QC to make comparison to different standard BIDS directory.

.. code-block:: console

  --qc_subdir QC_SUBDIR, -qs QC_SUBDIR
                        ExtraQC output directory name.


.. code-block:: console

   $ dicom_to_dpacc_bids.py \
       --input_dir PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/BW00001_MR_2021_07_22_1 \
       --subject_name BW00001 \
       --session_name 202107221 \
       --qc_subdir comparison_to_phantom \
       --output_dir MRI_ROOT \
       --standard_dir rawdata/sub-ProNETUCLA/ses-phantom \



.. _outputs:

----------------
Output structure
----------------

::

   MRI_ROOT/
   ├── sourcedata
   │   └── BW00001
   │       └── ses-202107221
   │           ├── 01_Localizer
   │           ├── ...
   │           └── 30_rfMRI_REST_PA
   ├── rawdata
   │   └── sub-BW00001
   │       └── ses-202107221
   │           ├── anat
   │           │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.json
   │           │   ├── ...
   │           │   └── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.nii.gz
   │           ├── dwi
   │           │   ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_dwi.bval
   │           │   ├── ...
   │           │   └── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_sbref.nii.gz
   │           ├── fmap
   │           │   ├── sub-BW00001_ses-202107221_acq-13_dir-AP_run-3_epi.json
   │           │   ├── ...
   │           │   └── sub-BW00001_ses-202107221_acq-8_dir-PA_run-2_epi.nii.gz
   │           ├── func
   │           │   ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-1_bold.json
   │           │   ├── ...
   │           │   └── sub-BW00001_ses-202107221_task-rest_dir-PA_run-2_sbref.nii.gz
   │           ├── ignore
   │           │   ├── sub-BW00001_ses-202107221_ignore-bids_num-1_localizer1.json
   │           │   ├── ...
   │           │   └── sub-BW00001_ses-202107221_ignore-bids_num-6_localizer_aligned3.nii.gz
   │           └── sub-BW00001_ses-202107221_scans.tsv
   └── derivatives
       ├── dwipreproc
       │   └── sub-BW00001
       │       └── ses-202107221
       ├── mriqc
       │   ├── sub-BW00001
       │   │   └── ses-202107221
       │   │       ├── anat
       │   │       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.json
       │   │       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.json
       │   │       │   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T1w.json
       │   │       │   └── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.json
       │   │       └── func
       │   │           ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-1_bold.json
       │   │           ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-2_bold.json
       │   │           ├── sub-BW00001_ses-202107221_task-rest_dir-PA_run-1_bold.json
       │   │           └── sub-BW00001_ses-202107221_task-rest_dir-PA_run-2_bold.json
       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.html
       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.html
       │   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T1w.html
       │   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.html
       │   ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-1_bold.html
       │   ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-2_bold.html
       │   ├── sub-BW00001_ses-202107221_task-rest_dir-PA_run-1_bold.html
       │   └── sub-BW00001_ses-202107221_task-rest_dir-PA_run-2_bold.html
       └── quick_qc
           └── sub-BW00001
               └── ses-202107221
                   ├── bval_comparison_log.txt
                   ├── csa_headers.csv
                   ├── json_check_image_orientation_in_anat.csv
                   ├── json_check_image_orientation_in_dMRI_fMRI_and_distortionMaps.csv
                   ├── json_check_shim_settings.csv
                   ├── json_comparison_log.txt
                   ├── scan_order.csv
                   ├── series_count.csv
                   ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_dwi.png
                   ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_sbref.png
                   ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-1_dwi.png
                   ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-1_sbref.png
                   ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_dwi.png
                   ├── sub-BW00001_ses-202107221_acq-b0_dir-AP_run-2_sbref.png
                   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.png
                   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T2w.png
                   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T1w.png
                   ├── sub-BW00001_ses-202107221_rec-norm_run-1_T2w.png
                   ├── summary_b0.png
                   ├── summary_dwi.png
                   ├── summary_fmri.png
                   ├── volume_slice_number_comparison_log.csv
                   └── within_phantom_qc.txt


