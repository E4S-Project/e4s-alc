===============
Supporting a new OS version
===============

This guide will walk you through supporting a new os version in ``e4s-alc``. 

.. contents:: 
   :depth: 3

--------------------
Updating the source code
--------------------

1. Whether it's done for a user's personal use or with the objective of creating a pull request, it is advised to first fork the ``e4s-alc``'s repository on github. More information on how to do so `here <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/working-with-forks/fork-a-repo>`_

2. After cloning the forked repository to our machine, we need to determine what packages this new OS version needs for ``e4s-alc`` to be able to build an image with it. This is as simple as attempting to create the image with ``e4s-alc`` and observe the packages whose absence/presence prevent the image from building.

    Let's take Rhel-ubi9 as our example OS:

    .. code:: terminal
        
        $ cat ubi9_test.yaml 
        ######## Base group ########
        backend: singularity
        registry: registry.access.redhat.com
        image: ubi9/ubi
        repull: True

        ####### Spack group #######
        spack: True
        spack-packages: 
          - tcl
        
        $ e4s-alc create -f ubi9_test.yaml
        [...]
        $ cat singularity.def
        Bootstrap: docker
        From: registry.access.redhat.com/ubi9/ubi

        %environment
            export DEBIAN_FRONTEND=noninteractive
            export PATH=/spack/bin:$PATH

        %files
        %post
            export DEBIAN_FRONTEND=noninteractive
            export PATH=/spack/bin:$PATH

            # Install OS packages
            yum update -y
            yum install -y findutils gcc-c++ gcc gcc-gfortran git xz gnupg2 hostname iproute make \
                patch bzip2 python3 python3-pip python3-setuptools unzip cmake vim \
                environment-modules

            # Install Spack version 0.22.0
            curl -L https://github.com/spack/spack/archive/refs/tags/v0.22.0/.tar.gz | tar xz && mv /spack-0.22.0 /spack

            # Setup spack and modules environment
            echo ". /etc/profile.d/modules.sh" >> /etc/profile.d/setup-env.sh && \
                echo ". /spack/share/spack/setup-env.sh" >> /etc/profile.d/setup-env.sh && \
                echo "export MODULEPATH=\$(echo \$MODULEPATH | cut -d':' -f1)" >> /etc/profile.d/setup-env.sh

            # Install Spack packages
            spack install tcl

            echo "spack compiler find" >> /etc/profile.d/setup-env.sh

        %startscript
            #!/bin/bash
            . /etc/profile.d/setup-env.sh && exec /bin/bash

        %runscript
            #!/bin/bash
            . /etc/profile.d/setup-env.sh && exec /bin/bash

    Then, when running the build command, we will see if the OS package list is fit for this OS version. If not, we can manipulate the list (in this case the one found in the ``yum install -y`` command).

    When this is done, we can update the source code to support this new list for this specific version.

3. We can use our prefered file editor to open ``/e4s-alc/e4s_alc/controller/image/rhel.py``.

    .. code:: python

        from e4s_alc.util import log_function_call, log_info
        from e4s_alc.controller.image.image import Image

        version_packages = { 
                'default': ['curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
                    'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch', 'bzip2',
                    'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
                '8.10': ['curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
                    'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch', 'bzip2',
                    'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
            }   

        class RhelImage(Image):
            """ 
            This class represents an object of Red Hat Enterprise Linux Image.
            Inherits from the Image base class.
            """

            @log_function_call
            def __init__(self, os_release):
                """
                Initialises the RhelImage with given OS release and
                sets the package manager commands, required packages and certificate details.

                Args:
                    os_release (str): Release version of the operating system.
                """
                super().__init__(os_release)
                self.pkg_manager_commands = None
                os_version = os_release["VERSION_ID"]
                if os_version in version_packages.keys():
                    self.packages = version_packages[os_version]
                else:
                    self.packages = version_packages["default"]
                self.update_cert_command = 'update-ca-trust'
                self.cert_location = '/etc/pki/ca-trust/source/anchors/'
               
                [...]

    As we can see, when initialisating the RhelImage object, we look at the os_version (that was deduces after analysing the pulled image) and then select the list of OS packages from a dictionary.
    All we need to do is determine the os_version and add an entry into the version_packages dictionary with that version as a key, and the list we previously determined as a value.

    .. note::
        The current dictionary has two keys with the same values, that is because ``e4s-alc`` started supporting rhel images with the 8.10 os_version, which makes it the 'default' list of os-packages. The distinction is kept in the code for clarity.

    One way to determine the os_version is to add a debugging command into the constructor:

    .. code:: python

            os_version = os_release["VERSION_ID"]
            import pdb;pdb.set_trace()
            if os_version in version_packages.keys():
                self.packages = version_packages[os_version]
            else:
                self.packages = version_packages["default"]

    After rebuilding ``e4s-alc``, running the create command from before will trigger a prompt that allows us to inspect the state of the execution, including variables.

    More information about pdb `here <https://docs.python.org/3/library/pdb.html>`_.

    In our case, the os_version is 9.4. Now we just have to add that entry to the dictionary:

    .. code:: python
        version_packages = { 
                'default': ['curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
                    'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch', 'bzip2',
                    'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
                '8.10': ['curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
                    'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch', 'bzip2',
                    'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
                '9.4': ['findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
                    'gnupg2', 'hostname', 'iproute', 'make', 'patch', 'bzip2',
                    'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
            }   
4. If we wish so, we can now push these changes to our forked repository of ``e4s-alc`` and start a pull request.
