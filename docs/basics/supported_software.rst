.. _alc_params:

===============
Supported Software
===============


.. contents:: 
   :depth: 3

``e4s-alc`` needs in-code implementations in order to support container technologies, as well as operating system. For the former, ``e4s-alc`` needs to implement the generation of the container definition file in the format of the container technology. For the latter, ``e4s-alc`` needs to implement the specifics of analysing the base image, as well as to know which os-packages need to be installed for the image building to function correctly.

---------------------
Container software
---------------------

~~~~~~~~~~~
``docker``
~~~~~~~~~~~

Docker container definition files, or Dockerfiles are supported, and ``e4s-al`` uses multistage building in them to make subsequent builds faster if one were to fail. Resulting images are managed by the docker deamon and available using its command line interface.

----

~~~~~~~~~~~~
``singularity``
~~~~~~~~~~~~

Singularity uses singularity definition files instead of Dockerfiles. ``e4s-alc`` doesn't support multistage building at the moment for singularity definition files. Also, singularity doesn't use a deamon, so the resulting images are created in place.

.. note::
    When building an image, the base image will be downloaded into ~/.e4s-alc/singularity_images in order to conduct analysis on it.

.. warning::
    This backend has a know issue with installing spack packages with gmake@4.4 when using singularity 3.11.0 (and doesn't with singularity 3.11.4). When this occurs, one can specify a dependency to gmake@4.3 for the related package:
    
    .. code-block::
    
     tcl => tcl ^gmake@4.3

----

~~~~~~~~~
``podman``
~~~~~~~~~

Podman container definition files use Dockerfiles. Regarding ``e4s-alc``, it behaves identically to docker.

----


-----------------------
Operating systems
-----------------------

Here is the list of supported operating systems and the specific versions for which the list of os-packages has been checked and fine-tuned.

.. note::
    When using a different version than one listed here under a specific OS, one might run into packages errors. One can work around these errors by updating the container definition file to remove/add the packages at the origin of the error.
..
    _this: You can see how to update the source code

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
``ubuntu``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* 20.04
* 22.04

----

~~~~~~~~~~~~~~~~
``rhel``
~~~~~~~~~~~~~~~~

* 8.10
* 9.4

----

~~~~~~~~~~~~~~~
``suse``
~~~~~~~~~~~~~~~

* 15.4

----

