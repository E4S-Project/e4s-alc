.. _qstart:

===========
Quick start
===========

The CLI tool is called **e4s-alc**. Before it can create/modify an image, it first needs to be set to one of the supported backends:
 * Podman
 * Docker
 * Singularity
   
Initialising the backend
-------------------------

.. code::

   $ e4s-alc init -b singularity
   Found singularity!
   Setting singularity as backend!
   $ cat ~/.e4s-alc/config.ini
   [DEFAULT]
   name = e4s-alc
   backend = singularity

When initialising **e4s-alc**, it will check for an installation of the desired backend on the local system, which is needed to create an image towards that backend.

.. admonition:: Default

   If no backend is specified, the default used backend will be Docker.

Creating an image
----------------------

Once a backend is setup through the **e4s-alc**'s initialisation, it can be use to create images seamlessly. An image to pull must be provided, as well as a name. Spack will be automatically installed (except if explicitely disabled through "--no-spack" flag), and Spack packages as well as OS packages can be installed.

Also, the command line instructions can be fed through a json file.

.. code::

    $ e4s-alc create \
        --image centos:8 \
        --name my-centos-image \
        -p py-numpy \
        -p autodiff

or

.. code::

    $ e4s-alc create \
        --image ubuntu:22.04 \
        --name my-ubuntu-image \
        --no-spack

or

.. code::

    $ cat test.json

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

    $ e4s-alc create -f test.json


