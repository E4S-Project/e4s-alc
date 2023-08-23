===========
Basic Usage
===========

``e4s-alc`` has 2 command line options. One command for creating the Dockerfiles and the other command for generating a ``.yaml`` template file that works with ``e4s-alc``. ``e4s-alc`` can take inputs as either parameters to the program call or through a file using the ``-f`` flag.

-----------
``e4s-alc``
-----------

.. code-block:: console

   $ e4s-alc -h
   usage: e4s-alc [command] [options]

   positional arguments:
     create      Create a Dockerfile
     template    Create a template file for e4s-alc

   options:
     -h, --help  show this help message and exit

------------------
``e4s-alc create``
------------------

Because building scientific packages is not easy, ``e4s-alc`` provides enough flags to ensure your build can become what you intend it to be with only 1 call. Below is the ``help`` display when you call for ``e4s-alc create``. We'll touch on what each of these flags do in the YAML Format section of the docs.

.. code-block:: console

   $ e4s-alc create -h 
   usage: e4s-alc create [options]
   
   options:
     -h, --help                    Display the help page
     -v, --verbose                 Verbose mode
   
   Load Arguments by file:
     -f, --file                    The file used to create a new image
   
   Base Stage Arguments:
     The base stage of the Dockerfile provides the foundation of the image.
   
     -b, --backend                 The container backend used for image inspection
     -i, --image                   The base image name <image:tag>
     -r, --registry                The image registry to search for the base image
     --env-variable                Set an environment variable inside the container
     --add-file                    Add a file to the container
     --initial-command             Commands to run after image is pulled
     --post-base-stage-command     Commands to run at the end of the base stage
   
   System Stage Arguments:
     The system stage of the Dockerfile provides important dependencies that the image might need.
   
     -crt, --certificate           Add an SSL certificate
     -a, --os-package              The name of an OS Package to install
     --add-remote-file             Add a remote file to the container
     --add-repo                    Clone a GitHub repository into the image
     --pre-system-stage-command    Commands to run at the beginning of the system stage
     --post-system-stage-command   Commands to run at the end of the system stage
   
   Spack Stage Arguments:
     The Spack stage of the Dockerfile provides Spack installations for the image.
   
     -s, --spack                   Choose to install spack
     --spack-version               The version of a Spack to install
     --spack-mirrors               The Spack mirror URL/Paths for Spack package caches.
     --spack-check-signature       Check for Spack package signature when installing packages from
                                   mirror
     --modules-yaml-file           The path to a modules.yaml environment file
     --spack-compiler              The Spack compiler that will be installed and will build Spack
                                   packages
     --spack-yaml-file             The path to a spack.yaml environment file
     -p, --spack-package           The name of a Spack package to install
     --pre-spack-stage-command     Commands to run at the beginning of the spack stage
     --post-spack-install-command  Commands to run after Spack is installed
     --post-spack-stage-command    Commands to run at the end of the spack stage
   
   Matrix Option Arguments:
     The matrix options allow users to build multiple Dockerfiles in one call with.
   
     --registry-image-matrix       The registry+image paths for each image to build
     --spack-version-matrix        The Spack version for each image to build
     --spack-compiler-matrix       The Spack compiler for each image to build
   

--------------------
``e4s-alc template``
--------------------

Running an ``e4s-alc create`` command with a lot of parameters can become messy. To organize the setup of your build, you can use ``e4s-alc create -f {file_name}.yaml`` to build out your Dockerfile. The ``e4s-alc template`` command outputs a template structure for your approach to creating a custom build. Each of these commands provide specific instructions for building out Dockerfile. Notice that ``registry-image-matrix``, ``spack-version-matrix``, and ``spack-compiler-matrix`` are in a group called ``Matrix group``. These are powerful parameters that allow the creation of multiple Dockerfiles in a single call. We'll go over them in the YAML Format section and the Tutorial at the end of the Basics section of the documentation.

.. code-block:: console

   $ e4s-alc template > template.yaml
   $ cat template.yaml
   ######## Base group ########
   backend:
   registry:
   image:
   
   initial-commands:
     -
   
   env-variables: 
     -
   
   add-files: 
     -
   
   post-base-stage-commands:
     -
   
   ######## System group ########
   pre-system-stage-commands: 
     -
   
   certificates:
     -
   
   os-packages: 
     -
   
   add-remote-files:
     -
   
   add-repos:
     -
   
   post-system-stage-commands: 
     -
   
   ####### Spack group #######
   spack: True
   pre-spack-stage-commands:
     -
   
   spack-version:
   spack-mirrors:
     -
   
   spack-check-signature: True
   modules-yaml-file: 
   post-spack-install-commands: 
     -
   
   spack-yaml-file: 
   spack-compiler:
   spack-packages: 
     -
   
   post-spack-stage-commands: 
     -
     
   ####### Matrix group #######
   registry-image-matrix:
     -
   
   spack-version-matrix:
     - 
   
   spack-compiler-matrix:
     -
