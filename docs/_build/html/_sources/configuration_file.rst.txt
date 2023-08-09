Configuration File
================

**E4S A-La-Carte** supports the use of json configuration files, which might be more convenient to some users.

Their use is only available for the **create** command, through the :code:`-f` flag.

Configuration options
------------------

The following options can be set in a configuration file:

.. list-table::
   :widths: 10 20 10 10
   :header-rows: 1
   
   * - Field
     - Description
     - Type
     - Default

   * - :code:`image`
     - The image and version to pull and base our new container from
     - Character string
     - :code:`""`

   * - :code:`name`
     - The name to give to the new image
     - Character string
     - :code:`""`

   * - :code:`spack`
     - Whether or not to install spack
     - Boolean
     - :code:`True`

   * - :code:`spack-packages`
     - The packages to install through spack
     - List of string
     - :code:`[]`

   * - :code:`os-packages`
     - The packages to install as os-packages
     - List of string
     - :code:`[]`

Examples
-------

Here is a configuration file example:

.. code-block::

   {
    "image": "ubuntu:22.04",
    "name": "test-file-kokkos-raja",
    "spack": true,
    "spack-packages": [
        "kokkos",
        "raja"
    ],
    "os-packages": [
        "neovim",
        "valgrind"
    ]
    }
