Installation
=====

.. _requirements:

Requirements
------------

- `dcm2niix` (>= version `v1.0.20210317`)

- `heudiconv` (>= version `v0.10.0`)

- `python3`

- `nifti_snapshot` (https://github.com/pnlbwh/nifti-snapshot)

- `numpy`, `pytest`, `pandas`, `matplotlib`, `nibabel`


Install dcm2niix
----------------

To use phantom_check, first install dcm2niix and add it to PATH variable.

.. code-block:: console

   $ export PATH=${PATH}:/PATH/TO/DCM2NIIX   # add to ~/.bashrc

Install phantom_check
---------------------

Install from github

.. code-block:: console

   $ git clone https://github.com/AMP-SCZ/phantom_check
   $ cd phantom_check

   $ pip install heudiconv[all]
   $ pip install -r requirements.txt


Add the path to ``~/.bashrc``

.. code-block:: console

   # path settings
   export PATH=${PATH}:~/phantom_check/scripts

