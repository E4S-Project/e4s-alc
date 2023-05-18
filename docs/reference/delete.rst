**delete** - Delete images
==========================

This command deletes specified images.

Usage
----

.. code::
   $ e4s-alc delete [ OPTIONS ]

Options
------

Either the **name** parameter, **prune-images** parameter or **prune-container** parameter is required 

-n, --name              Name of the images to delete, or list of images to delete
-c , --container        ID of the container to delete
-f, --force             Attempt to force the deletion
--prune-images          Delete unused images [docker]
--prune-containers      Delete stopped containers [docker, podman]

Description
---------

Going through the selected backend's api, **E4S A-La-Carte** will delete the image given as argument. It can also prune idle images and stopped containers, depending if the backend supports it.
