===================
Development Notes
===================

- Kevin Cho
- Nicholas Kim
- Owen Borders
- Ofer Pasternak

.. _initial_development:

-------------------
Initial development
-------------------

Quick-QC (QQC) begun as a simple python script used for detecting changes in
BIDS json sidecar files between a newly acquired MRI data and the previoously
acquired phantom data. Since more quality control measures were required to
assess the newly acquired data in more depth, the dicom to BIDS conversion
pipeline and different image preprocessing pipelines were added to QQC. Also,
as the number of data points increased, the presentation layer had to be
developed, in addition to a form of database of the reports. These needs
led QQC to have different modules and made it expand from a simple code to a
pipeline. During this process, DPACC invested a significant resources in
developing QQC, and investing further effort to make the tool able to be used
by other scientific institutions. We hope to share our experience in curating a
large multi-site MRI study through QQC.


.. _new_developments:

------------------------
New ongoing developments
------------------------

- Database
    - Manual QC pipelines
        - APIs to communicate with Google spreadsheet
- Visualization
    - DPDash


.. _development_training_notes:

--------------------------
Development training notes
--------------------------

The following section documents the basic concept and skills useful for
collaborating on the development.


Understanding QQC pipeline
--------------------------

- :ref:`standard_templates`

- `Tutorial <tutorial.html>`_


Github Basics
-------------

- `Push and Request <github_push_request.html>`_


Testing
-------

- `Test running QQC <test_running_qqc.html>`_
- `Missing data check <missing_data_check.html>`_


Neuroimaging Bascis
-------------------

- :ref:`dcm2niix`


Coding environment 
------------------

- `Vim settings for ERIS <vim_settings_for_eris.html>`_

