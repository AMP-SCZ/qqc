Welcome to Phantom_check's documentation!
=========================================

**Phantom_check** is a Python library for converting U24 MRI dicoms to BIDS 
format and running quick quality check (QC) pipelines. 


#. Copy and clean up the dicoms according to unique series number and names
#. Convert dicoms to BIDS nifti using `heudiconv <https://heudiconv.readthedocs.io/en/latest/>`_
#. Quick QC pipeline

   * Compares series information to another template BIDS datasource.

   * MRIQC

   * FMRIPREP

      * Freesurfer

   * Quick diffusion preprecssing

      * Topup

      * Eddy

      * eddy_squeeze

      * MKCurve

Check out the :doc:`installation` and :doc:`usage` section for further 
information.

.. note::

   This project is under active development.


Contents
--------

.. toctree::

   installation
   usage
   steps_in_detail
   qqc_outputs
