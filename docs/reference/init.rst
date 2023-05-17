**init** - Initialize the backend
==============================

This command initialises the backend to use to generate images for. It checks all necessary software is available to use the specified backend and sets it as the automatic backend to use for subsequent commands.

Usage
-----

.. code-block::

   e4s-alc init [ OPTIONS ]

Options
------

-b, --backend     Backend for containers
-h, --help

.. admonition:: Default behavior
   If no backend is specified through the **backend** flag, then docker will be used as the backend to be selected.

Description
----------

Checks for the required backend, the corresponding python api library's availability and the ability for the client to connect. This being done, it writes in :code:`~/.e4s-alc/config.ini` the selected backup.
