=========================
Tutorial: ``e4s-alc`` 101
=========================

This tutorial assumes that you have installed ``e4s-alc``, you have all the dependancies, and that the binary can be located in your ``PATH``.

----------------------------------------------------
1. Installing ``hwloc`` and ``cmake`` on Rocky Linux
----------------------------------------------------

For the first tutorial, I want to demonstrate the actions you could perform in order to build Spack loaded images on the fly using only the command line tool.

Imagine a client needs a Rocky Linux 9 image loaded with ``hwloc`` and ``cmake`` for a project. 

To start fresh, we'll create a new directory called ``MyProject`` and we'll work inside of it.

.. code-block:: console

   $ mkdir MyProject && cd MyProject

The components we need for this project are broken down into:

| 1. A base image (Rocky Linux 9)
| 2. Spack packages (``hwloc`` and ``cmake``)

We would run the following code:

.. code-block:: console

   $ e4s-alc create \
        --image rockylinux:9 \ 
        --spack-package hwloc \
        --spack-package cmake

This produces our Dockerfile!

.. code-block:: console

   $ ls
   Dockerfile

Using ``podman``, let's build, run, and inspect our image:

.. code-block:: console 

   $ podman build -t example1 . && podman run -it example1
   [root@de58aafb6377 /]# module avail
   ---------------- /modulefiles/linux-rocky9-zen2 -----------------
   cmake/3.26.3  hwloc/2.9.1  

   Key:
   modulepath  
   [root@de58aafb6377 /]# spack find
   ==> In environment main
   ==> Root specs
   cmake  hwloc

   ==> Installed packages
   -- linux-rocky9-zen2 / gcc@11.3.1 -------------------------------
   berkeley-db@18.1.40                 cmake@3.26.3   hwloc@2.9.1        libsigsegv@2.14  m4@1.4.19       perl@5.36.0    util-macros@1.19.3
   bzip2@1.0.8                         diffutils@3.9  libiconv@1.17      libtool@2.4.7    ncurses@6.4     pkgconf@1.9.5  xz@5.4.1
   ca-certificates-mozilla@2023-01-10  gdbm@1.23      libpciaccess@0.17  libxml2@2.10.3   openssl@1.1.1t  readline@8.2   zlib@1.2.13
   ==> 21 installed packages

-----------------------------------------------------------------------
2. Installing ``hwloc`` and ``cmake`` on Rocky Linux using ``gcc@11.2``
-----------------------------------------------------------------------

We finalized the project for the client and they were happy until they realized that they forgot an important part of the image description... It has to be built using ``gcc@11.2``. No problem. 

We'll use a similar call to the last example but we'll insert a ``spack-compiler`` flag:

.. code-block:: console 

   $ e4s-alc create \
        --image rockylinux:9 \ 
        --spack-compiler gcc@11.2 \
        --spack-package hwloc \
        --spack-package cmake

Let's build, run, and inspect the image:

.. code-block:: console 

   $ podman build -t example2 . && podman run -it example2


--------------------
3. Using YAML files!
--------------------

.. code-block:: console 

   This section is in progress.
