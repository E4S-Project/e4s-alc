**create** - Create an image
===========================

This command creates an image using the backend set up with the **init** command. It will pull a specified image, install the specified packages, set up given tarballs and directories and then commit these to a new image.

Usage
----

.. code-block::

   e4s-alc create [options]

Options
------

Only the **name** and **image** arguments are required, or they can be replaced by a configuration file through the **file** argument.

-i, --image         The image name and the tag <image:tag>
-n, --name          The name of the image to add to
-p, --package       The name of a Spack package to install
-a, --os-package    The name of an OS Package to install
-c, --copy          Directory to copy into the image
-t, --tarball       Tarball to expand in the image
-f, --file          The file used to add to a image
-P, --parent        Specific to singularity backend, choose which backend to use between Podman and Docker ["podman", "docker"] to add to the image

Description
-------

**E4S A-La-Carte** will pull the requested image and run an instance of it. It will then run commands that apply the changes requested through the command line options. Then the current backend will commit the changes to the image.

This is very similar to the image addition workflow: **create** allows to modify an image not yet locally available, but every customisation available through it can be achieved in through the **add** command.
