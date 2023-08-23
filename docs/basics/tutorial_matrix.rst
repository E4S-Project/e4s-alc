==============================
Tutorial: ``e4s-alc`` matrices
==============================

In the context of ``e4s-alc``, matrices refer to the generation of multiple Dockerfiles with largely identical attributes, with only a few parameters varying between each. Essentially, this allows us to construct several Dockerfiles that are almost identical, but have variations in the following parameters:

* ``image``
* ``spack-compiler``
* ``spack-version``

To put it simply, using matrices in ``e4s-alc`` enables us to build diverse Dockerfiles by only altering key parameters, while keeping the remaining elements consistent.

----------------------------------
1. Using ``registry-image-matrix``
----------------------------------

For example, I have following ``.yaml`` file and I want to make this setup for both ``ubuntu:20.04`` and ``rocklinux:9``:
 
.. code-block:: console 

   $ cat input.yaml
   image: rockylinux:9
   spack-compiler: gcc@11.2
   spack-packages:
     - tau@2.32

To create 2 Dockerfiles I would modify the ``image`` parameter to:

.. code-block:: console 

   $ cat input.yaml
   registry-image-matrix: 
     - ubuntu:20.04
     - rockylinux:9
   spack-compiler: gcc@11.2
   spack-packages:
     - tau@2.32

After running ``e4s-alc create -f input.yaml``, I get a new directory called ``dockerfiles``:

.. code-block:: console 

   $ ls
   dockerfiles  input.yaml
   $ ls dockerfiles
   Dockerfile.rocky9.2-spack0.20.1-gcc11.2
   Dockerfile.ubuntu20.04-spack0.20.1-gcc11.2

----------------------------------------------------------------
2. Using ``registry-image-matrix`` and ``spack-compiler-matrix``
----------------------------------------------------------------

Imagine we want to determine whether the operating system and the compiler contribute to the runtime performance of an application. 

The operating systems we are testing are:

* ``ubuntu:20.04``
* ``rockylinux:9``

The compilers we are testing are:

* ``gcc11.2``
* ``intel-oneapi-compilers``

The combinations of systems we would need to set up are:

* ``ubuntu:20.04`` with ``gcc11.2``
* ``ubuntu:20.04`` with ``intel-oneapi-compilers``
* ``rockylinux:9`` with ``gcc11.2``
* ``rockylinux:9`` with ``intel-oneapi-compilers``

This is where ``e4s-alc`` can greatly help you. We can create a ``.yaml`` file with the following specs:

.. code-block:: console 

   $ cat input.yaml
   registry-image-matrix: 
     - ubuntu:20.04
     - rockylinux:9
   spack-compiler-matrix:
     - gcc@11.2
     - intel-oneapi-compilers 
   spack-packages:
     - tau@2.32

After running ``e4s-alc create -f input.yaml``, the new directory ``dockerfiles`` contains:

.. code-block:: console

   $ ls dockerfiles
   Dockerfile.rocky9.2-spack0.20.1-gcc11.2
   Dockerfile.rocky9.2-spack0.20.1-oneapilatest
   Dockerfile.ubuntu20.04-spack0.20.1-gcc11.2
   Dockerfile.ubuntu20.04-spack0.20.1-oneapilatest
