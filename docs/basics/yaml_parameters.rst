.. _yaml_params:

===============
YAML Parameters
===============

.. contents:: 
   :depth: 3

---------------------
Base Group Parameters
---------------------

~~~~~~~~~~~
``backend``
~~~~~~~~~~~

| **Type**: ``string``
| **Description**: The container backend that will be used for gathering information about the base image operating system.
| **Example**:

.. code-block:: console

   backend: podman

----

~~~~~~~~~~~~
``registry``
~~~~~~~~~~~~
| **Type**: ``string``
| **Description**: The hosted service where images will be pulled from. This parameter is optional but defaults to ``docker.io/library``.
| **Example**:

.. code-block:: console

   registry: registry.access.redhat.com

----

~~~~~~~~~
``image``
~~~~~~~~~

| **Type**: ``string``
| **Description**: The image that will be pulled from the registry. This image will serve as the base image of the Dockerfile. 
| **Example**:

.. code-block:: console

   image: ubi8/ubi


| **Note**: If the ``registry`` is not specified, ``image`` may also take the combined registry-image form:

.. code-block:: console

   image: registry.access.redhat.com/ubi8/ubi

----

~~~~~~~~~~~~~~~~~~~~
``initial-commands``
~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to be ran immediately after the image has been pulled. This parameter is optional.
| **Example**:

.. code-block:: console

   initial-commands:
     - cat /etc/os-release > os_release_info.txt
     - uname -a > system_info.txt

----

~~~~~~~~~~~~~
``add-files``
~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The files that will be copied into the image. Each entry must take the form ``<source> <destination_directory>``. This copies the host ``<source>`` **TO** the image ``<destination_directory>``. This parameter is optional. 
| **Example**:

.. code-block:: console

   add-files:
     - project_dir /project_dir    
     - inputs.txt /data/

| **Note**: The ``<source>`` path must be inside the context of the build. Because the first step of a container build is to send the context directory to the container daemon, you cannot use the form ``- ../something /something``.
| **Note**: If the extension of ``<source>`` is ``.tgz`` or ``.tar.gz`` then the file will be unpacked and placed in ``<destination_directory>``.
----

~~~~~~~~~~~~~~~~~
``env-variables``
~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The environment variables to be set inside of the image. This parameter is optional.
| **Example**:

.. code-block:: console

   env-variables:
     - PROJECT_ROOT=/project_dir
     - PROJECT_INPUTS=/data/inputs.txt

| **Note**: By default, ``e4s-alc`` adds the Spack binary, ``spack``, to ``PATH``.

----

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``post-base-stage-commands``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to run after files have been added and environment variables have been set. This parameter is optional.
| **Example**:

.. code-block:: console

   post-base-stage-commands:
     - ls /project_dir
     - cat $PROJECT_INPUTS

----

-----------------------
System Group Parameters
-----------------------

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``pre-system-stage-commands``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to run before starting the System Group. These commands immediately follow ``post-base-stage-commands`` and may provide a modular approach to the image build. This parameter is optional.
| **Example**:

.. code-block:: console

   pre-system-stage-commands:
     - printenv

----

~~~~~~~~~~~~~~~~
``certificates``
~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The certificates to add into the image. These certificates will be used to establish secure HTTPS connections to servers with certificates issued by globally recognized CA. This parameter is optional.
| **Example**:

.. code-block:: console

   certificates:
     - certs/company-root-ca.pem
     - certs/techlabs-ca.crt

----

~~~~~~~~~~~~~~~
``os-packages``
~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The additional OS packages to install into the image. By default, the image will install the system `prerequisites <https://spack.readthedocs.io/en/latest/getting_started.html>`__ for Spack based on the OS package manager. This parameter is optional.
| **Example**:

.. code-block:: console

   os-packages:
     - valgrind
     - neovim

----


~~~~~~~~~~~~~~~
``add-remote-files``
~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: Similar to the parameter, ``add-files`` except instead of using a local file as the ``<source>``, the ``<source>`` is a URL to a file. This parameter will download the file to the ``<destination_directory>``. This parameter is optional.
| **Example**:

.. code-block:: console

   add-remote-files:
     - http://tau.uoregon.edu/tau.tgz /opt/

----

| **Note**: If the extension of ``<source>`` is ``.tgz`` or ``.tar.gz`` then the file will be unpacked and placed in ``<destination_directory>``.


~~~~~~~~~~~~~~~
``add-repo``
~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The GitHub repos to be cloned into the image. This parameter is optional.
| **Example**:

.. code-block:: console

   add-repo:
     - https://github.com/MyProject/packages.git /opt/packages
     - https://github.com/MyProject/packages.git --branch development

----


~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``post-system-stage-commands``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to run after the System Group have been completed. This parameter is optional.
| **Example**:

.. code-block:: console

   post-system-stage-commands:
     - ls /opt/packages

----

----------------------
Spack Group Parameters
----------------------

~~~~~~~~~
``spack``
~~~~~~~~~

| **Type**: ``bool``
| **Description**: Whether the Spack Group should be executed or not. Default is `True`. Choosing `False` will result in the image being finalized.
| **Example**:

.. code-block:: console

   spack: True

----

~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``pre-spack-stage-commands``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to run before starting the Spack Group. These commands immediately follow ``post-system-stage-commands`` and may provide a modular approach to the image build. This parameter is optional.
| **Example**:

.. code-block:: console

   pre-spack-stage-commands:
     - valgrind --version

----

~~~~~~~~~~~~~~~~~
``spack-version``
~~~~~~~~~~~~~~~~~

| **Type**: ``{int}.{int}.{int}`` or ``string``
| **Description**: The version of Spack to be installed. Choosing ``latest`` will install the latest version of Spack.
| **Example**:

.. code-block:: console

   spack-version: 0.20.1

----

~~~~~~~~~~~~~~~~~
``spack-mirrors``
~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: A list of Spack build caches to be added to Spack. This parameter is optional.
| **Example**:

.. code-block:: console

   spack-mirrors:
     - https://cache.e4s.io

----

~~~~~~~~~~~~~~~~~~~~~~~~~
``spack-check-signature``
~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``bool``
| **Description**: Whether or not Spack should check the signatures of the packages being downloaded from a Spack Mirror. This parameter is optional.
| **Example**:

.. code-block:: console

   spack-check-signature: False

----

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``post-spack-install-commands``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to run after Spack has been installed and the mirrors have been installed. This parameter is optional.  
| **Example**:

.. code-block:: console

   post-spack-install-commands:
     - spack --version
     - spack mirror list

----

~~~~~~~~~~~~~~~~~~~~~
``modules-yaml-file``
~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``string``
| **Description**: The path to a ``modules.yaml`` file that will help configure the layout and usage of ``module``. This parameter is optional but defaults to downloading this `modules.yaml <https://www.nic.uoregon.edu/~cfd/e4s-alc/modules.yaml>`__
| **Example**:

.. code-block:: console

   modules-yaml-file: ./modules.yaml

----

~~~~~~~~~~~~~~~~~~~
``spack-yaml-file``
~~~~~~~~~~~~~~~~~~~

| **Type**: ``string``
| **Description**: The path to the ``spack.yaml`` file that will be used to install Spack packages. If this flag is used, ``e4s-alc`` will not install packages using the ``spack-packages`` parameter. This parameter is optional.
| **Example**:

.. code-block:: console

   spack-yaml-file: ./spack.yaml

----

~~~~~~~~~~~~~~~~~~
``spack-compiler``
~~~~~~~~~~~~~~~~~~

| **Type**: ``string``
| **Description**: The name of the compiler to install and the compiler to use for Spack package installation. This parameter is optional but the default compiler will be used if this is not specified.
| **Example**:

.. code-block:: console

   spack-compiler: gcc@11.2

----

~~~~~~~~~~~~~~~~~~
``spack-packages``
~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The list of Spack package to install. This parameter is optional.
| **Example**:

.. code-block:: console

   spack-packages:
     - tau@2.32
     - hwloc
     - kokkos

----

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``post-spack-stage-commands``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The commands to be ran after the Spack Group is complete. This parameter is optional. 
| **Example**:

.. code-block:: console

   post-spack-stage-commands:
     - spack find

----

-----------------------
Matrix Group Parameters
-----------------------

The Matrix Group parameters are used when multiple Dockerfiles are desired. Using group parameters will create ``len(registry-image-matrix) * len(spack-version-matrix) * len(spack-compiler-matrix)`` Dockerfiles.

~~~~~~~~~~~~~~~~~~~~~~~~~
``registry-image-matrix``
~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The images that you'd like to create a Dockerfile for. If this parameter is specified, do not specify the neither ``registry`` nor ``image`` parameter.
| **Example**:

.. code-block:: console

   registry-image-matrix:
     - ubuntu:20.04
     - rockylinux:9

----

~~~~~~~~~~~~~~~~~~~~~~~~
``spack-version-matrix``
~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<{int}.{int}.{int} | string>``
| **Description**: The Spack versions that you'd like to create a Dockerfile for. If this parameter is specified, do not specify the ``spack-version`` parameter.
| **Example**:

.. code-block:: console

   spack-version-matrix:
     - latest
     - 0.20.0
     - 0.19.2

----

~~~~~~~~~~~~~~~~~~~~~~~~~
``spack-compiler-matrix``
~~~~~~~~~~~~~~~~~~~~~~~~~

| **Type**: ``list<string>``
| **Description**: The Spack compilers that you'd like to create a Dockerfile for. If this parameter is specified, do not specify the ``spack-compiler`` parameter.
| **Example**:

.. code-block:: console

   spack-compiler-matrix:
     - gcc@11.2
     - intel-oneapi-compilers
