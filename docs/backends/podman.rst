Podman
======

The Podman backend is currently supported through this `python package <https://pypi.org/project/podman/>`_. You can find it's source code through this `link <https://github.com/containers/podman-py>`_.

Description
------

All utilities of **E4S A-La-Carte** for the Podman backend use the local podman daemon. This means that the local podman installation and **e4s-alc** access the same images, and all **e4s-alc** commands ultimately will be run by the local docker podman.
