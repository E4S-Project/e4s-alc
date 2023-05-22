Singularity
=========

The Singularity backend is currently supported through the Docker or Podman backend. The Singularity image format prevents modifying image without superuser privileges, so **E4S A-La-Carte** instead uses another backend to pull the image, apply modifications and then builds it to a singularity file format.

Description
-------

Singularity images can be created/added-to through either docker or podman's client. This is specified by the user through the :code:`--parent` flag (default backend used is docker). The creation/addition process will happen entirely through the alternate backend and then the image will be converted to the singularity image format.

.. warning::

   In order to add to a singularity image generated through **e4s-alc**, the image pulled by the original alternate backend must be still available.
   In addition, you cannot add to a singularity image if the image wasn't created through **e4s-alc**.

Singularity not functionning through a locally running daemon also means that the images are accessible through the user's file system. Specifically, they will appear in the :code:`.e4s-alc/singularity_images` directory, which by default is in the user's home directory. 

When referencing to a singularity image in the **e4s-alc** cli, the name should omit the ".sif" file extension, appart when deleting it.
