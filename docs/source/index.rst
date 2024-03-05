Welcome to Quick Quality Check's documentation!
=========================================

**Quick Quality Check** (QQC) is a Python-based tool designed to identify protocol deviations in newly acquired MRI scans.

Initially, QQC organizes DICOM files by their series number and description from the DICOM headers. It then calls Heudiconv, which utilizes dcm2niix, to automatically convert DICOM files into NIFTI files, aligning with predefined BIDS structure file naming conventions. An example of the BIDS structure can be found in Figure 1 (https://github.com/AMP-SCZ/ampscz_mri_upload#example-structure).

Following conversion, QQC compares the new MRI data against reference data from the same site—usually a pilot scan or the study's initial scan, already verified by the research team. This comparison checks every detail in the BIDS sidecar JSON files, with any discrepancies highlighting protocol adjustments. QQC further examines the number of diffusion weighting directions and values, as well as volumes and slices across all images, identifying any conversion errors, partial transfers, or incomplete scans.

QQC visually summarizes MRI scans by generating snapshots, GIFs of the NIFTI data, and plots of mean intensity across volumes. A comprehensive HTML report summarizing these comparisons and visual summaries is then emailed to the team, allowing for quick assessment of the new data. This end-to-end process, from receiving new data to dispatching the summary report, takes less than 20 minutes per MRI session, enabling rapid identification and rectification of protocol deviations.

Moreover, QQC is adaptable to run various preprocessing pipelines like fMRIPrep, MRIQC, Freesurfer, or bespoke in-house pipelines. It can compare the output of these pipelines to standards or averages from other studies (e.g., the Human Connectome Project), pinpointing individual deviations in imaging metrics like volume, functional ROI correlations, and fractional anisotropy.



Requirements for Utilizing QQC:
-------------------------------
#. Configuration of the Heudiconv heuristic file.

  Heudiconv configuration file is required to run heudiconv on your dataset. Please follow `hediconv documentation <https://heudiconv.readthedocs.io/en/latest/>`_
  to create a heudiconv configuration file specific for your scan.

  An example of the heudiconv configuration file is available `here <https://github.com/AMP-SCZ/qqc/blob/main/data/heuristic.py>`_.

#. A template MRI scan serving as the comparison standard.
#. The dcm2niix tool available in the operating environment.


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
