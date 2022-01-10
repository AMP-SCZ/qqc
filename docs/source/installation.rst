Installation
============

.. _dcm2niix:

Install dcm2niix
----------------

To use phantom_check, first install
`dcm2niix <https://github.com/rordenlab/dcm2niix>`_ and add it to PATH
variable.

.. code-block:: shell

   export PATH=${PATH}:/PATH/TO/DCM2NIIX
   echo "export PATH=${PATH}:/PATH/TO/DCM2NIIX" > ~/.bashrc


.. _dcm2niix:

Install heudiconv
-----------------

``heudiconv`` is also required to run ``phantom_check``. Install ``heudiconv``
following the `instruction on their website <https://heudiconv.readthedocs.io/en/latest/installation.html>`_,
and make sure you can access ``heudiconv`` from your console.

.. code-block:: shell

   heudiconv -h



.. _install_phantom_check:

Install phantom_check
---------------------

Install from ``pip``

.. code-block:: shell

   pip install phantom_check


or install from github

.. code-block:: shell

   git clone https://github.com/AMP-SCZ/phantom_check
   cd phantom_check

   pip install heudiconv[all]  #installing heudiconv
   pip install -r requirements.txt


.. note::
   if you used git to clone ``phantom_check``, add the script path to your
   ``~/.bashrc``

   .. code-block:: shell

       echo "export PATH=${PATH}:~/phantom_check/scripts" >> ~/.bashrc

