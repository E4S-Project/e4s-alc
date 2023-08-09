.. _install:

Installation
================

From the Python Package Index
------------------------------

Install **e4s-alc** using the python package system:

.. code-block:: bash

   $ pip install e4s-alc


From source
-------------


To install a version from the sources, first clone the repository:

.. code-block:: bash

    $ git clone https://github.com/E4S-Project/e4s-alc

Program installation
*********************

Install **e4s-alc** using :code:`make install`. The installation directory can be modified using the :code:`INSTALLDIR` variable:

.. code-block:: bash

    $ INSTALLDIR=<prefix> make install
..
The **e4s-alc** program will be copied over to :code:`<prefix>/bin`. On success, a message will be printed with the full path to add to your :code:`PATH`.

A python interpreter will be downloaded to ensure a compatible Python 3 version is available.
