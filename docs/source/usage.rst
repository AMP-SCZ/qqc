Usage
=====

Running the Docker Container
----------------------------

To execute the Docker container, use the following command:

.. code-block:: shell

   docker run \
     -v /absolute/path/to/ROOT/OF/INPUT_DICOM:/data/dicom \
     -v /absolute/path/to/MRI_ROOT:/data/output \
     -v /absolute/path/to/BIDS/SESSION/OF/STANDARD/DATA:/data/standard \
     qqc \
     qqc.py \
         --input_dir /data/dicom \
         --subject_name SubjectName \
         --session_name SessionName \
         --output_dir /data/output \
         --standard_dir /data/standard

Details on Docker Command Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. **Docker Volume Binding (``-v`` or ``--volume``)**
   Binds a host system directory to a container directory, granting the container access to host data for both input and output operations.

   - **Input Directory** (``--input_dir``): Bind the directory containing DICOM files.
   - **Output Directory** (``--output_dir``): Bind the directory for storing output data.
   - **Standard Directory** (``--standard_dir``): Bind the directory of the BIDS session for protocol comparison.

2. **Docker Image Name**: Specify the image name (``qqc``) after volume bindings.

3. **Command and Options**: Include the `qqc.py` command with relevant options as they are to be executed within the container.


Executing the Singularity Container
-----------------------------------

.. code-block:: shell

   singularity exec \
     --bind /absolute/path/to/ROOT/OF/INPUT_DICOM:/data/dicom \
     --bind /absolute/path/to/MRI_ROOT:/data/output \
     --bind /absolute/path/to/BIDS/SESSION/OF/STANDARD/DATA:/data/standard \
     /path/to/qqc.sif \
     qqc.py \
         --input_dir /data/dicom \
         --subject_name SubjectName \
         --session_name SessionName \
         --output_dir /data/output \
         --standard_dir /data/standard

Details on Singularity Command Options
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Singularity command options are used similarly to Docker for executing containers but with some syntax differences:

1. **Singularity Bind Option (``--bind``)**
   This option maps host system directories to directories within the container, similar to Docker's volume binding.

   - **Input Directory** (``--input_dir``): Use the ``--bind`` option to map the directory containing DICOM files into the container.
   - **Output Directory** (``--output_dir``): Map the directory designated for output data storage into the container.
   - **Standard Directory** (``--standard_dir``): Map the BIDS session directory for protocol comparison into the container.

2. **Singularity Image File**: Specify the path to the Singularity image file (`.sif`) instead of an image name.

3. **Executing the Command**: After specifying the image file and binding options, include the `qqc.py` command with associated options as intended for execution within the Singularity environment.


Local Execution of ``qqc.py``
-----------------------------

To process all DICOM files under a specified directory and compare them with another BIDS directory for protocol discrepancies, utilize the following command:

.. code-block:: shell

   qqc.py \
       --input_dir ROOT/OF/DICOM_DIR \
       --subject_name SubjectName \    # without 'sub-'
       --session_name SessionName \    # without 'ses-'
       --output_dir OUTPUT/DIR/ROOT \
       --standard_dir BIDS/SESSION/OF/STANDARD/DATA

This command will store the outputs under ``MRI_ROOT``.

Command Options for ``qqc.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **``--input_dir``**: Accepts any structured directory containing DICOM files.
- **``--subject_name``**: Utilize the subject ID; ``sub-`` prefix will be automatically appended.
- **``--session_name``**: Specify the date and unique label number, omitting spaces, `-`, or `_`.
- **``--output_dir``**: Designates the root directory for outputs, where ``sourcedata``, ``rawdata``, and ``derivatives`` directories will be generated.
- **``--standard_dir``**: Indicates the root of the BIDS session for protocol comparison.


Extra Quality Control Options
-----------------------------

- **Extra QC Comparison**:

  .. code-block:: console

     --qc_subdir QC_SUBDIR, -qs QC_SUBDIR
                           Extra QC output directory name.


Output Structure
----------------

The output structure is organized as follows, facilitating easy access and analysis:

.. code-block:: none

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


