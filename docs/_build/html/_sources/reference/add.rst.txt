**add** - Add to an image
=====================

Add packages, tarballs and/or directories to an available image.

Usage
----

.. code-block::

   e4s-alc add [ OPTIONS ]

Options
------

Only the **name** argument is required, but without any other argument the command will have no effect.

-n, --name          The name of the image to add to
-p, --package       The name of a Spack package to install
-y, --yaml          The yaml file used to specify a spack environment to install
-a, --os-package    The name of an OS Package to install
-c, --copy          Directory to copy into the image
-t, --tarball       Tarball to expand in the image
-f, --file          The file used to add to a image
-P, --parent        Specific to singularity backend, choose which backend to use between Podman and Docker ["podman", "docker"] to add to the image

Description
-------

**E4S A-La-Carte** will run an instance of the specified image and run commands that apply the changes requested through the command line options. Then the current backend will commit the changes to the image.

This is very similar to the image creation workflow: **add** simply allows to modify an image that is already available, but every customisation available through it can be achieved in through the **create** command.
