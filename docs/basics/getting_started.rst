===============
Getting Started
===============

This guide will walk you through the basics of using our tool. 
We'll cover everything from system prerequisites to how the software works.

.. contents:: 
   :depth: 3

--------------------
System Prerequisites
--------------------

Before installing and running this program, make sure that your system meets the following prerequisites:

1. ``make``: This utility is available in the majority of Unix-like operating systems by default. If it's not installed on your system, you can install it from the official package repository. For example, on Debian-based distributions, you can use ``sudo apt install make``.

2. ``wget`` or ``curl``: These are frequently used command-line tools for sending HTTP requests. Most Unix-based systems include them by default. If they are not installed, you can install either of them using your system's package manager. For instance, ``sudo apt install wget`` or ``sudo apt install curl``.

3. **Container backend** (``docker`` or ``podman``): The program requires a container backend to run. You can choose between Docker, Podman. Please follow the official installation instructions for the particular backend you choose to install:

    - For Docker: https://docs.docker.com/engine/install/
    - For Podman: https://podman.io/getting-started/installation
  
4. **Internet connection**: The program needs an active internet connection to function correctly. Please ensure your device is connected to the internet before initializing the program.

Please keep in mind that to install the aforementioned system prerequisites and to run the program itself, you may require administrative (``sudo``) rights on your system.

------------
Installation
------------

To install ``e4s-alc``, you need to perform these commands in terminal:

1. Clone the E4S-alc repository from GitHub using the command below:

.. code-block:: console

   $ git clone https://github.com/E4S-Project/e4s-alc.git

2. Navigate to the cloned directory and run the ``make install`` command:

.. code-block:: console

   $ cd e4s-alc && make install

After running this command, you should see several messages indicating the progress of the installation:

.. code-block:: console

   Downloading Miniconda...Complete!
   Installing python packages...Complete!
   Installing e4s-alc through pip...Complete!

These messages show that the Makefile is automatically performing several steps: downloading Miniconda, installing some Python packages required for ``e4s-alc``, and then installing ``e4s-alc`` itself using ``pip``, the Python package installer.

3. Finally, you're instructed to add ``e4s-alc`` to your PATH environment variable. You can accomplish this by running the following command:

.. code-block:: console

   $ export PATH=$(pwd)/e4s-alc-v1.0.0/bin:$PATH

All together

.. code-block:: console

   $ git clone https://github.com/E4S-Project/e4s-alc.git
   $ cd e4s-alc && make install
   $ export PATH=$(pwd)/e4s-alc-v1.0.0/bin:$PATH

And with that, installation is complete! You should now be able to use ``e4s-alc`` from your terminal. Remember to run the export command in each new terminal session, or add it to your ``.bashrc`` or ``.bash_profile`` file to make this change permanent.


-------------
Quick Example
-------------

The following command creates a Dockerfile using an ``ubuntu:22.04`` base image preconfigured to install Spack and download ``zlib``:  

.. code-block:: console

   $ e4s-alc create \
          --image ubuntu:22.04 \
          --spack-package zlib

The corresponding Dockerfile is shown below. You may notice that the Dockerfile has indented syntax (Docker doesn't recommend this formatting but it provides readability) and is broken up into multiple stages, we'll break this Dockerfile down in the following section.

.. code-block:: Dockerfile

   # Base Stage
   FROM ubuntu:22.04 AS base-stage
   
           # Set up the environment
           ENV DEBIAN_FRONTEND=noninteractive
           ENV PATH=/spack/bin:$PATH
   
   # System Stage
   FROM base-stage AS system-stage
   
           # Install OS packages
           RUN apt-get update
           RUN apt-get install -y build-essential ca-certificates coreutils curl file \
               environment-modules gfortran git gpg lsb-release vim python3 \
               python3-distutils python3-venv unzip zip cmake
   
   # Spack Stage
   FROM system-stage AS spack-stage
   
           # Install Spack version 0.20.1
           RUN curl -L https://github.com/spack/spack/releases/download/v0.20.1/spack-0.20.1.tar.gz | tar xz && mv /spack-0.20.1 /spack
   
           # Setup spack and modules environment
           RUN echo ". /etc/profile.d/modules.sh" >> /etc/profile.d/setup-env.sh && \
               echo ". /spack/share/spack/setup-env.sh" >> /etc/profile.d/setup-env.sh && \
               echo "export MODULEPATH=\$(echo \$MODULEPATH | cut -d':' -f1)" >> /etc/profile.d/setup-env.sh && \
               echo "spack env activate main" >> /etc/profile.d/setup-env.sh
   
           # Add modules.yaml file
           RUN curl https://www.nic.uoregon.edu/~cfd/e4s-alc/modules.yaml -o /spack/etc/spack/modules.yaml
   
           # Create a Spack environment
           RUN spack env create main
   
           # Install Spack packages
           RUN . /spack/share/spack/setup-env.sh && spack env activate main && spack install --add zlib
   
           # Update compiler list
           RUN spack compiler find
   
   # Finalize Stage
   FROM spack-stage AS finalize-stage
   
           # Entrypoint of the image
           ENTRYPOINT ["/bin/bash", "-c", ". /etc/profile.d/setup-env.sh && exec /bin/bash"]
   
---------------
Workflow Stages
---------------

The sequential structure of the Dockerfile is crucial, as each stage is dependent on the one preceding it. For example, if the Base Stage specifies ``rockylinux:9`` instead of ``ubuntu:22.04``, the System Stage would utilize the package manager ``yum`` instead of ``apt``. This structure provides a maintaining dynamic functionality that ``e4s-alc`` adapts based on the input parameters. 

``e4s-alc`` also provides options for running commands before and after each stage. This makes workflow customization simple for build complex systems.

~~~~~~~~~~
Base Stage
~~~~~~~~~~

.. code-block:: Dockerfile

   # Base Stage
   FROM ubuntu:22.04 AS base-stage

           # Set up the environment
           ENV DEBIAN_FRONTEND=noninteractive
           ENV PATH=/spack/bin:$PATH

The base stage of the Dockerfile serves as the foundation on which the succeeding stages build. It involves picking an appropriate base image (in this case, ``Ubuntu:22.04``) and setting up the necessary environment variables. This stage is vital because it forms the fundamental operating system layer in which applications will run. Any changes to this stage may significantly affect the whole Docker build process and the applications running within the Docker containers.

~~~~~~~~~~~~
System Stage
~~~~~~~~~~~~

.. code-block:: Dockerfile

   # System Stage
   FROM base-stage AS system-stage
   
           # Install OS packages
           RUN apt-get update
           RUN apt-get install -y build-essential ca-certificates coreutils curl file \
               environment-modules gfortran git gpg lsb-release vim python3 \
               python3-distutils python3-venv unzip zip cmake

Following the base-stage, the system-stage further builds on the base image by installing additional utilities and packages needed for the specific use-case of the Docker image. These packages provide essential functionalities to enable system operations, developer utilities or runtime of applications. This stage helps to customize the image to meet specific requirements.

~~~~~~~~~~~
Spack Stage
~~~~~~~~~~~

.. code-block:: Dockerfile

   # Spack Stage
   FROM system-stage AS spack-stage
   
           # Install Spack version 0.20.1
           RUN curl -L https://github.com/spack/spack/releases/download/v0.20.1/spack-0.20.1.tar.gz | tar xz && mv /spack-0.20.1 /spack
   
           # Setup spack and modules environment
           RUN echo ". /etc/profile.d/modules.sh" >> /etc/profile.d/setup-env.sh && \
               echo ". /spack/share/spack/setup-env.sh" >> /etc/profile.d/setup-env.sh && \
               echo "export MODULEPATH=\$(echo \$MODULEPATH | cut -d':' -f1)" >> /etc/profile.d/setup-env.sh && \
               echo "spack env activate main" >> /etc/profile.d/setup-env.sh

           # Add modules.yaml file
           RUN curl https://www.nic.uoregon.edu/~cfd/e4s-alc/modules.yaml -o /spack/etc/spack/modules.yaml

           # Create a Spack environment
           RUN spack env create main

           # Install Spack packages
           RUN . /spack/share/spack/setup-env.sh && spack env activate main && spack install --add zlib

           # Update compiler list
           RUN spack compiler find

The Spack stage is about setting up the Spack package manager and related dependencies. The Spack manager automates the process of downloading, building, and installing packages along with their dependencies. This stage simplifies the process of managing multiple packages, handling dependencies, and ensuring that the correct versions of packages are used. 

~~~~~~~~~~~~~~
Finalize Stage
~~~~~~~~~~~~~~

.. code-block:: Dockerfile

   # Finalize Stage
   FROM spack-stage AS finalize-stage

           # Entrypoint of the image
           ENTRYPOINT ["/bin/bash", "-c", ". /etc/profile.d/setup-env.sh && exec /bin/bash"]

The finalize stage is the concluding stage in the Dockerfile where the image is finalized for use. This simplifies the process of initializing a Docker container from the final image, making it straightforward to run and handle. It also serves as a point where any cleanup or optimizations can be carried out to reduce the size of the final Docker image.


-------------------------
Running the Example Image
-------------------------

.. code-block:: console

   $ e4s-alc create \
          --image ubuntu:22.04 \
          --spack-package zlib

Following the completion of the command above, a Dockerfile appears in the current working directory.

.. code-block:: console

   $ ls
   Dockerfile

Using ``podman`` (for example), I build and run the image with:

.. code-block:: console

   $ podman build . -t example-image && podman run -it example-image

Now I'm in the image. Now let's check our spack packages with ``spack find``. Notice how an environment has already been created for our specs.

.. code-block:: console

   root@d67d168212a0:/# spack find
   ==> In environment main
   ==> Root specs
   zlib

   ==> Installed packages
   -- linux-ubuntu22.04-zen2 / gcc@11.4.0 --------------------------
   zlib@1.2.13
   ==> 1 installed package

The container comes with Environment Modules so we can easily load and unload installed packages with ``module``. Let's list our available modules and load ``zlib``:

.. code-block:: console

   root@d67d168212a0:/# module avail
   ------- /modulefiles/linux-ubuntu22.04-zen2 -------
   zlib/1.2.13  

   Key:
   modulepath  
   root@d67d168212a0:/# module load zlib
   root@d67d168212a0:/# ls $ZLIB_LIB
   libz.a  libz.so  libz.so.1  libz.so.1.2.13  pkgconfig

------------
How It Works
------------

``e4s-alc`` operates by receiving a set of inputs in the form of a command line call. Once these inputs are processed, ``e4s-alc`` initiates the process of pulling the designated base image. Following this, the content of the base image is analyzed to confirm its compatibility with the succeeding stages.

Upon completion of the analysis, ``e4s-alc`` shifts into the building phase. It commences the systematic construction of each stage, ensuring that the commands utilized in each stage align correctly with the given inputs and the base image. This iterative construction ensures the resulting Dockerfile maintains compatibility throughout all stages.
