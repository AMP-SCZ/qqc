Welcome to Quick-QC's documentation!
=========================================

**Quick-QC** (QQC) is a Python library for detecting protocol deviations in
each newly acquired MRI dataset for a study. The main functions of QQC are

#. Finds deviations in the newly acquired data.
#. Clean up the dicom files.
#. Convert to BIDS nifti using `heudiconv <https://heudiconv.readthedocs.io/en/latest/>`_.
#. Executes different MRI QC pipelines.
#. Curates the report of each new MRI data into different databases.


.. note::
   QQC is under an active development in the AMP-SCZ project.


Contents
--------

.. toctree::

   installation
   usage
   steps_in_detail
   qqc_outputs
   development_notes
