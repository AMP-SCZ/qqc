Installation
=====

.. _requirements:

Requirements
------------

- dcm2niix (>= version v1.0.20210317)
- heudiconv (>= version v0.10.0)
- python3
- `nifti_snapshot <https://github.com/pnlbwh/nifti-snapshot>`_
- matplotlib==3.0.3
- nibabel==3.1.0
- numpy==1.16.2
- pandas==0.24.2
- pydicom==1.3.0
- pytest==5.4.3
- scikit_learn==1.0.2
- seaborn==0.11.1


.. _dcm2niix:

Install dcm2niix
----------------

To use phantom_check, first install dcm2niix and add it to PATH variable.

.. code-block:: console

   $ export PATH=${PATH}:/PATH/TO/DCM2NIIX   # add to ~/.bashrc


.. _install_phantom_check:

Install phantom_check
---------------------

Install from github

.. code-block:: console

   $ git clone https://github.com/AMP-SCZ/phantom_check
   $ cd phantom_check

   $ pip install heudiconv[all]  #installing heudiconv
   $ pip install -r requirements.txt


Add the path to ``~/.bashrc``

.. code-block:: console

   export PATH=${PATH}:~/phantom_check/scripts  # path settings

