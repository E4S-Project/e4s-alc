.. _UserDir:

==================
User Directory
==================

**e4s-alc** uses a user directory to store user specific data. This article describes the different directories withing it.

Configuration File
------------------

**config.ini** is a simple configuration file that currently simply holds the value for the backend currently in use eg:

.. code::

   $ cat ~/.e4s-alc/config.ini

   [DEFAULT]
   name = e4s-alc
   backend = docker

Spack Environment Files
-----------------------

**spack_yamls** holds the spack environment files. If you want to use a yaml file configuring a spack environment to configure an image, you need to copy that file into this directory and then specify the file name using the command line interface at image creation or addition.

Singularity Images
------------------

**singularity_images** holds the singularity images created through **e4s-alc**. As **Singularity** functions without a locally running daemon, **e4s-alc** keeps its images at a specific location to avoid losing track of them. Other supported backend technologies have a locally run daemon and handle their own images.

Podman Tarballs
---------------

With **e4s-alc**, you need either **Docker** or **Podman** support to generate **Singularity** images. Indeed, **Singularity** doesn't have the ability to commit modified images in a container instance. Instead, we commit an image pulled and modified with **Docker** or **Podman** (**Podman** being the default but **Docker** can be used instead, through the **--parent** flag), and then generate a **Singularity** image from it.

When using **Podman** as a parent, it will create a tarball of the image as a step to generate the **Singularity** image, and store it in the **podman_tarballs** directory.
