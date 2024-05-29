=========================
Tutorial: ``e4s-alc`` 101
=========================

This tutorial assumes that you have installed ``e4s-alc`` and the binary can be located in your ``PATH``.

=========================
Creating a Dockerfile
=========================

----------------------------------------------------
1. Installing ``hwloc`` and ``cmake`` on Rocky Linux
----------------------------------------------------

For the first tutorial, we will walk through the commands to build Spack-loaded images on the fly using only the command line tool.

Imagine we need a Rocky Linux 9 image loaded with ``hwloc`` and ``cmake`` for a project. 

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

For this example, the Spack packages have to be built using ``gcc@11.2`` and we want ``tau`` downloaded to ``/opt``. 

We'll use a similar call to the previous example but we'll insert a ``spack-compiler`` parameter and ``add-remote-file`` parameter:

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
3. Using a YAML|JSON file
--------------------

For organization and quick reproducibility, we may want to use an input file to specify parameters instead of specifying the parameters in the command line. To start, let's rewrite the previous ``e4s-alc`` command in the form of an ``e4s-alc`` compatible ``.yaml`` file. We have:

.. code-block:: console 

   $ e4s-alc create \
        --image rockylinux:9 \ 
        --spack-compiler gcc@11.2 \
        --spack-package hwloc \
        --spack-package cmake \
        --add-remote-file "http://tau.uoregon.edu/tau.tgz /opt"


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

Transformed to a ``.json`` file, we have:

.. code-block:: console

   $ cat input.json
   {
    "image": "rockylinux:9",
    "add-remote-files": [
        "http://tau.uoregon.edu/demo.tgz /opt"
    ],
    "spack-compiler": "gcc@11.2",
    "spack-packages": [
        "hwloc",
        "cmake"
    ]
   }
   $ e4s-alc create -f input.json

For more information on the ALC parameters, visit :ref:`ALC Parameters <alc_params>`.

=========================
Creating a Singularity definition file
=========================

From the user's side, creating a Singularity image with e4s-alc will be very similar to creating a Docker/Podman image. We simply havw to specify the use of the singularity backend to do so:

.. code-block:: console

   $ e4s-alc create \
        --backend singularity \
        --image rockylinux:9 \
        --spack-package hwloc \
        --spack-package cmake

This works the same way than for creating a Dockerfile, except it will output a Singularity definition file:

.. code-block:: console

   $ ls
   singularity.def

Then we can use singularity to build, run and inspect our image:

.. code-block:: console

   $ singularity build example.sif singularity.def
   [...]
   $ singularity run example.sif
   Singularity> spack find
    -- linux-rocky9-zen3 / gcc@11.4.1 -------------------------------
    berkeley-db@18.1.40                 diffutils@3.10      gmake@4.3          libxml2@2.10.3  perl@5.38.0         zlib-ng@2.1.6
    bzip2@1.0.8                         findutils@4.9.0     hwloc@2.9.1        m4@1.4.19       pkgconf@2.2.0
    ca-certificates-mozilla@2023-05-30  gcc-runtime@11.4.1  libpciaccess@0.17  ncurses@6.5     readline@8.2
    cmake@3.27.9                        gdbm@1.23           libsigsegv@2.14    nghttp2@1.57.0  util-macros@1.19.3
    curl@8.7.1                          glibc@2.34          libtool@2.4.7      openssl@3.3.0   xz@5.4.6
    ==> 26 installed packages

.. warning::

    In the case we don't have sudo access, this previous build command would fail, as Singularity needs sudo writes to build an image from a definition file. Thankfully, Singularity provides a ``fakeroot`` option that allows an unprivileged user to run a container as a "fake root" user. This requires the user to be listed in the ``/etc/subuid`` and ``/etc/subgid`` (which requires administrator access to modify). More information `here <https://docs.sylabs.io/guides/3.3/user-guide/fakeroot.html>`_.

    When doing so, our command will look like this:

    .. code-block:: console

       $ singularity build --fakeroot example.sif singularity.def


We can also use an input file instead of using the CLI to create a Singularity definition file, which is advised for ease of use.
Here is the same previous example translated into a ``yaml`` file:

.. code-block:: console

   $ cat input.yaml
   backend: singularity
   image: rockylinux:9
   spack-packages:
     - hwloc
     - cmake

.. note::

    When running ``e4s-alc create``, we pull the base image to run analysis on it. For the Docker and Podman backend, the image location is handled by them. But when pulling a singularity image, its location is handled by ``e4s-alc`` and stored in ``~/.e4s-alc/singularity_images`` under a [os]_[version].sif naming convention.


    Before pulling the image, ``e4s-alc`` will check if the image can be found in its local collection using the same naming convention. 
    If the image is found in the local collection, ``e4s-alc`` will prompt the user to choose between keeping the image and pulling it again. This prompt can be pre-answered using the :ref:`repull<alc_params>` parameter.

    .. warning::

        It is possible for two different images to fall under the same name, for example when using ``latest`` as the needed version.
