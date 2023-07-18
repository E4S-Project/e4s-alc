.. _qstart

===========
Quick start
===========

The CLI tool is called **e4s-alc**. Before it can create/modify an image, it first needs to be set to one of the supported backends:
 * Podman
 * Docker
 * Singularity
   
Initializing the backend
-------------------------

.. code::

   $ e4s-alc init -b singularity
   Found singularity!
   Setting singularity as backend!
   $ cat ~/.e4s-alc/config.ini
   [DEFAULT]
   name = e4s-alc
   backend = singularity

When initializing **e4s-alc**, it will check for an installation of the desired backend on the local system, which is needed to create an image towards that backend.

.. admonition:: Note

   If no backend is specified, the default used backend will be Docker.

Creating an image
----------------------

Once a backend is setup through the **e4s-alc**'s initialization, it can be use to create images seamlessly. An image to pull must be provided, as well as a name. Spack will be automatically installed (except if explicitely disabled through :code:`--no-spack` flag), and Spack packages as well as OS packages can be installed.

Also, the command line instructions can be fed through a json file.

.. code::

    $ e4s-alc create \
        --image centos:8 \
        --name my-centos-image \
        -p py-numpy autodiff

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

If you have a spack environment file (spack.yaml), you can provide it to **e4s-alc** by placing it in the :ref:`**e4s-alc user directory** <UserDir>` subdirectory named **spack_yamls**. Then, when creating an image (or adding to an image), specify the file's name through the **-y/--yaml** flag to have the environment installed:


.. code::

   $ ls ~/.e4s-alc/spack_yamls/
   spack.yaml  test_spack.yaml

   $ e4s-alc create \
   --image ubuntu:22.04 \
   --name spack_environment_image \
   --yaml spack.yaml

Adding to an image
------------------

Once an image is created (through **e4s-alc** or not), it can be updated with new os-packages and/or spack packages through a new call:

.. code::

   $ e4s-alc add -n my-ubuntu-image -p kokkos -a neovim

If you want to use a spack environment file to add to an image, it is supported and done the same way than for the image creation.

Listing available images
---------------------------

After creating images, they can be listed with the **list** command:

.. code::

   $ e4s-alc create -i ubuntu -n my-ubuntu-image
   $ e4s-alc list
   +-----------------+--------+--------------+----------------------+------------+
   |       Name      |  Tag   |      Id      |       Created        |    Size    |
   +-----------------+--------+--------------+----------------------+------------+
   | my-ubuntu-image | latest | 70ee2ea5dc24 | 05/15/2023, 20:16:49 | 604.99 MiB |
   |      ubuntu     | latest | 3b418d7b466a | 04/25/2023, 17:30:49 | 74.21 MiB  |
   +-----------------+--------+--------------+----------------------+------------+

.. admonition:: Note

   Only the images created from the currently initialised backend will be shown. To list images from another backend, you should first run :code:`e4s-alc init -b other_backend`

Deleting images
---------------

Images can also be removed by using the **delete** command:

.. code::

   $ e4s-alc list
   +-----------------+--------+--------------+----------------------+------------+
   |       Name      |  Tag   |      Id      |       Created        |    Size    |
   +-----------------+--------+--------------+----------------------+------------+
   | my-ubuntu-image | latest | 70ee2ea5dc24 | 05/15/2023, 20:16:49 | 604.99 MiB |
   |      ubuntu     | latest | 3b418d7b466a | 04/25/2023, 17:30:49 | 74.21 MiB  |
   +-----------------+--------+--------------+----------------------+------------+
   $ e4s-alc delete -n ubuntu
   $ e4s-alc list
   +-----------------+--------+--------------+----------------------+------------+
   |       Name      |  Tag   |      Id      |       Created        |    Size    |
   +-----------------+--------+--------------+----------------------+------------+
   | my-ubuntu-image | latest | 70ee2ea5dc24 | 05/15/2023, 20:16:49 | 604.99 MiB |
   +-----------------+--------+--------------+----------------------+------------+
