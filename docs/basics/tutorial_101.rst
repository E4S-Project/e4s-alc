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

We finalized the project for the client and they were happy until they realized that they forgot an important part of the image description... The Spack packages have to be built using ``gcc@11.2`` and wants ``tau`` downloaded to ``/opt`` . No problem. 

We'll use a similar call to the last example but we'll insert a ``spack-compiler`` parameter and ``add-remote-file`` parameter:

.. code-block:: console 

   $ e4s-alc create \
        --image rockylinux:9 \ 
        --spack-compiler gcc@11.2 \
        --spack-package hwloc \
        --spack-package cmake \
        --add-remote-file "http://tau.uoregon.edu/tau.tgz /opt"

Let's build, run, and inspect the image:

.. code-block:: console 

   $ podman build -t example2 . && podman run -it example2
   [root@1b92e0f8ee2a /]# module avail
   ---------------- /modulefiles/linux-rocky9-zen2 -----------------
   cmake/3.26.3  gcc/11.2.0  hwloc/2.9.1  
   
   Key:
   modulepath  
   [root@1b92e0f8ee2a /]# spack find
   ==> In environment main
   ==> Root specs
   cmake  hwloc
   
   ==> Installed packages
   -- linux-rocky9-zen2 / gcc@11.2.0 -------------------------------
   berkeley-db@18.1.40  ca-certificates-mozilla@2023-01-10  diffutils@3.9  hwloc@2.9.1    libpciaccess@0.17  libtool@2.4.7   m4@1.4.19    openssl@1.1.1t  pkgconf@1.9.5  util-macros@1.19.3  zlib@1.2.13
   bzip2@1.0.8          cmake@3.26.3                        gdbm@1.23      libiconv@1.17  libsigsegv@2.14    libxml2@2.10.3  ncurses@6.4  perl@5.36.0     readline@8.2   xz@5.4.1
   ==> 21 installed packages
   [root@1b92e0f8ee2a /]# ls /opt
   tau-2.32
   
--------------------
3. Using a YAML file
--------------------

For organization and quick reproducibility, we may want to use a ``.yaml`` file to specify parameters instead of specifying the parameters in the command line. To start, let's rewrite the previous ``e4s-alc`` command in the form of an ``e4s-alc`` compatible ``.yaml`` file. We have:

.. code-block:: console 

   $ e4s-alc create \
        --image rockylinux:9 \ 
        --add-remote-file "http://tau.uoregon.edu/tau.tgz /opt" \
        --spack-compiler gcc@11.2 \
        --spack-package hwloc \
        --spack-package cmake


Transformed to a ``.yaml`` file, we have:

.. code-block:: console 

   $ cat input.yaml
   image: rockylinux:9
   add-remote-files:
     - http://tau.uoregon.edu/demo.tgz /opt
   spack-compiler: gcc@11.2
   spack-packages:
     - hwloc
     - cmake
   $ e4s-alc create -f input.yaml

For more information on the ``.yaml`` parameters, visit :ref:`YAML Parameters <yaml_params>`.
