===================
Quick Quality Check
===================

.. _qqc_outputs:

-------------------
List of QQC outputs
-------------------
- ``series_count.csv``: This shows the comparison of unique series number 
  compared to the standard BIDS session. Look for any extra or missing series.

.. image:: images/series_count.png
   :width: 300

- ``json_comparison_log.xlsx``: compare input dcm2niix sidecar jsons to
  json in tempalte BIDS data.

.. image:: images/json_comparison_log.png
   :width: 600

- ``json_comparison_log.txt``: same as above in a text format.

- ``volume_slice_number_comparison_log.csv``: This table shows the shape of
  each nifti array, and compares to matching nifti file under the given
  standard BIDS session. Look for any unmatched labels. (``False`` in the
  ``check`` column)

.. image:: images/volume_slice_number_comparison_log.png
   :width: 500
  
- ``scan_order.csv``: check order of series acquisitions against template 
  BIDS data.

.. image:: images/series_order.png
   :width: 300

- ``bval_comparison_log.txt``: compare b-values and number of shells in DWI
  against template BIDS data.

.. image:: images/bval_comparison_log.png
   :width: 500

- ``within_phantom_qc.txt``: compare consistency across series in a same
  session

.. image:: images/within_phantom_qc.png
   :width: 600

The same information is included in the tables below.

- ``json_check_image_orientation_in_anat.csv``
- ``json_check_image_orientation_in_dMRI_fMRI_and_distortionMaps.csv``
- ``json_check_shim_settings.csv``

- ``csa_headers.csv``: extract extra CSA header information for each series.

.. image:: images/csa_headers.png
   :width: 600

- ``summary_b0.png``
- ``summary_dwi.png``
- ``summary_fmri.png``

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
