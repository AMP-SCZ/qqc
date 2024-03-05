Installation
============

.. _dockerized_version:

Use docker
-----------------------
TBA

Go to setups


.. _singularity_version:

Use singularity
-----------------------
TBA

Go to setups



.. _dcm2niix:

Install dcm2niix
----------------

To use qqc, first install
`dcm2niix <https://github.com/rordenlab/dcm2niix>`_ and add it to PATH
variable.

.. code-block:: shell

   export PATH=${PATH}:/PATH/TO/DCM2NIIX
   echo "export PATH=${PATH}:/PATH/TO/DCM2NIIX" > ~/.bashrc


.. _dcm2niix:

Install heudiconv
-----------------

``heudiconv`` is also required to run ``qqc``. Install ``heudiconv``
following the `instruction on their website <https://heudiconv.readthedocs.io/en/latest/installation.html>`_,
and make sure you can access ``heudiconv`` from your console.

.. code-block:: shell

   heudiconv -h



.. _install_qqc:

Install qqc
---------------------

Install from ``pip``

.. code-block:: shell

   pip install qqc


or install from github

.. code-block:: shell

   git clone https://github.com/AMP-SCZ/qqc
   cd qqc

   pip install heudiconv[all]  #installing heudiconv
   pip install -r requirements.txt


.. note::
   if you used git to clone ``qqc``, add the script path to your
   ``~/.bashrc``

   .. code-block:: shell

       echo "export PATH=${PATH}:~/qqc/scripts" >> ~/.bashrc

