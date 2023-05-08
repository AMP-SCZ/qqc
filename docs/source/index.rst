Welcome to Phantom_check's documentation!
=========================================

**Quick Quality Check** (QQC) is a Python library for checking protocol deviations in the incoming MRI data for cohort studies.


QQC applies the following stpes to the new MRI data.

#. Copy and clean up the dicoms according to unique series number and description.
#. Convert dicoms to BIDS nifti using `heudiconv <https://heudiconv.readthedocs.io/en/latest/>`_
#. Find deviations in the new data

   * Compares dicom and nifti information to the template BIDS datasource.

#. Executes preprocessing pipelines.

   * MRIQC

   * FMRIPREP

      * Freesurfer

   * Quick diffusion preprecssing

      * Unring
      * Topup
      * Eddy


Requirements
------------

- Heudiconv configuration file

  Heudiconv configuration file is required to run heudiconv on your dataset. Please follow `hediconv documentation <https://heudiconv.readthedocs.io/en/latest/>`_
  to create a heudiconv configuration file specific for your scan.

  An example of the heudiconv configuration file is available `here <https://github.com/AMP-SCZ/qqc/blob/main/data/heuristic.py>`_.


Check out the :doc:`installation` and :doc:`usage` section for further 
information.

.. note::

   This project is under active development.


Add-on functions
----------------

There are new features addded to QQC that have not been documented yet.

* MRI flow tracker
  QQC was initiated to be used in the `AMP SCZ <https://www.ampscz.org/>`_ project, in which more than 4000 MRI scans were anticipated. There are ongoing effort by
  the members of `DPACC <https://www.ampscz.org/about/networks-coordination/>`_ to track, investigate, and report about all available scans.
    * Asana Pipeline (Omar John and Simone Veale)
      Uses `Asana <https://asana.com/>`_ API to visually track MRI dataflow and QQC progress. This visualization is deprecated due to the team's decision to use DPDash,
      but many of the codes developed moved to Backend Database project below.
    * Backend Database (Owen Borders and Nicholas Kim)
      There is an ongoing effort in creating daily upated database of all existing MRI data and expected MRI data according
      to the REDCap and RPMS (the survey database used in AMP SCZ study). This pipeline labels which data is missing at DPACC,
      and which data is processed through QQC, providing an all-in-one database that could be used in visualization
      softwares.
* Google-spreadsheet reporter (Nicholas Kim)
  In addition to the automatic quality checks done by QQC, our team also visually checks all incoming data for quality 
  control and curates the information to a google spreadsheet. Using the Google API, QQC progress will be pushed
  to the same google spreadsheet and the manual quality control scores will be pulled to the server to the backend database.


Contents
--------

.. toctree::

   installation
   usage
   steps_in_detail
   qqc_outputs
