Singularity
=========

The Singularity backend is currently supported through the Docker or Podman backend. The Singularity image format prevents modifying image without superuser privileges, so **E4S A-La-Carte** instead uses another backend to pull the image, apply modifications and then builds it to a singularity file format.
