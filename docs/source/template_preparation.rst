A Template MRI Scan Serving as the Comparison Standard
======================================================

Setting Up Directories to Save Data
------------------------------------

First, set up the directories where the data will be saved:

.. code-block:: shell

   export MRI_ROOT=/path/to/save/all/data
   mkdir -p $MRI_ROOT/rawdata $MRI_ROOT/sourcedata $MRI_ROOT/derivatives

Arranging the Template MRI Scan
-------------------------------

To curate the template MRI data in a BIDS format compatible with QQC, run `qqc/scripts/qqc.py` with the `--template` option. The template MRI scan must have been acquired with the correct protocol and be of good quality, as it will serve as the standard for comparison against incoming data throughout the duration of the study.

.. code-block:: shell

   qqc/scripts/qqc.py --template /path/to/template/dicom/data 

Creating the Template Configuration File (Optional)
---------------------------------------------------

If managing multiple studies with differing protocols or machines, it is possible to use a configuration file. This file directs each new dataset to a specific template.

.. code-block:: shell

   [Studies]
   StudyA = /path/to/MRI_ROOT/rawdata/sub-studyA/ses-pilot1
   StudyB = /path/to/MRI_ROOT/rawdata/sub-studyB/ses-pilot1
   StudyC = /path/to/MRI_ROOT/rawdata/sub-studyC/ses-pilot1
   StudyD = /path/to/MRI_ROOT/rawdata/sub-studyD/ses-pilot1

