Usage
=====

.. _usage:

``dicom_to_dpacc_bids.py``
--------------------------

To process all dicom files under a dicom directory, and compare them to another
BIDS directory for any protocol differences, use the command below.

.. code-block:: shell

   dicom_to_dpacc_bids.py \
       --input_dir ROOT/OF/DICOM_DIR \
       --subject_name SubjectName \    # without 'sub-'
       --session_name SessionName \    # without 'ses-'
       --output_dir OUTPUT/DIR/ROOT \
       --standard_dir BIDS/SESSION/OF/STANDARD/DATA


This wll save the outputs under ``MRI_ROOT``.

#. ``--input_dir`` can virtually take any form of structure as long as there
   are dicom files under the directory.

    * eg) ``PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/BW00001_MR_2021_07_22_1``

#. For ``--subject_name``, use the subject ID. ``sub-`` prefix will be attached
   in front of the given subject name.

    * eg) ``--subject_name BW00001``

#. For ``--session_name``, use the date and unique label number without any
   spaces, `-`, or `_`. 

    * eg) ``--session_name 202107221``

#. ``--output_dir`` is the root directory of the output. This path is where 
   ``sourcedata``, ``rawdata`` and ``derivatives`` directories will be created.

    * eg) ``-output_dir MRI_ROOT``

#. ``--standard_dir`` is the root of **BIDS session** that you would like to
   compare the protocols of the ``--input_dir``.

    * eg) ``rawdata/sub-ProNETUCLA/ses-phantom``


.. _available_options:

Available options
-----------------

#. Run extra QC to make comparison to different standard BIDS directory.

.. code-block:: console

  --qc_subdir QC_SUBDIR, -qs QC_SUBDIR
                        ExtraQC output directory name.


.. code-block:: shell

   dicom_to_dpacc_bids.py \
       --input_dir PHOENIX/PROTECTED/PronetLA/raw/BW00001/mri/BW00001_MR_2021_07_22_1 \
       --subject_name BW00001 \
       --session_name 202107221 \
       --qc_subdir comparison_to_phantom \
       --output_dir MRI_ROOT \
       --standard_dir rawdata/sub-ProNETUCLA/ses-phantom \



.. _outputs:

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
   │           │   └── ...
   │           ├── dwi
   │           │   ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_dwi.bval
   │           │   └── ...
   │           ├── fmap
   │           │   ├── sub-BW00001_ses-202107221_acq-13_dir-AP_run-3_epi.json
   │           │   └── ...
   │           ├── func
   │           │   ├── sub-BW00001_ses-202107221_task-rest_dir-AP_run-1_bold.json
   │           │   └── ...
   │           ├── ignore
   │           │   ├── sub-BW00001_ses-202107221_ignore-bids_num-1_localizer1.json
   │           │   └── ...
   │           └── sub-BW00001_ses-202107221_scans.tsv
   └── derivatives
       ├── dwipreproc
       │   └── sub-BW00001
       │       └── ses-202107221
       ├── fmriprep
       ├── mriqc
       │   ├── sub-BW00001
       │   │   └── ses-202107221
       │   │       ├── anat
       │   │       └── func
       │   ├── sub-BW00001_ses-202107221_rec-nonnorm_run-1_T1w.html
       │   └── ...
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
                   ├── summary_b0.png
                   ├── summary_dwi.png
                   ├── summary_fmri.png
                   ├── volume_slice_number_comparison_log.csv
                   ├── within_phantom_qc.txt
                   ├── sub-BW00001_ses-202107221_acq-176_dir-PA_run-1_dwi.png
                   └── ...


