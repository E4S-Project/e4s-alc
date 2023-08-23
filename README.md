# E4S à la Carte

## Description

E4S à la Carte is a practical tool designed to facilitate the generation of Dockerfiles infused with OS packages, Spack packages, as well as custom commands. In the simplifying the process, this tool targets the elimination of manual Dockerfile scripting, enabling users to concentrate on critical aspects such as application-specific resources and configurations. 

## Documentation

Our documentation is located here: <a href="https://e4s-alc.readthedocs.io/en/latest/" target="_blank">Documentation</a>

## Overview

The `e4s-alc` tool is designed to facilitate the process of crafting Dockerfiles. This tool leverages `.yaml` files as input to generate Dockerfiles.

## Installation

Installing `e4s-alc` is simple.

Clone the project:
```
git clone https://github.com/E4S-Project/e4s-alc.git
```

Run `make`:
```
cd e4s-alc && make install
```

## Example 

Here is an example `.yaml` file. This input file creates a Dockerfile using a Rhel8 base image. It installs gcc@11.2 and installs kokkos using gcc@11.2. Notice how I've chosen to exclude parameters to fit my build. This is one of the example `.yaml` files in the `examples` directory.

```
# rhel8-gcc11.2-kokkos.yaml

######## Base group ########
backend: podman
registry: registry.access.redhat.com
image: ubi8/ubi

####### Spack group #######
spack-version: latest
spack-compiler: gcc@11.2
spack-packages:
  - kokkos
```

I build the Dockerfile and image with:

```
e4s-alc create -f rhel8-gcc11.2-kokkos.yaml
podman build .
``` 

Then, run the image in interactive mode and inspect the install:

```
[root@c5ad0d45ba1d /]# module avail
----------------------------- /modulefiles/linux-rhel8-power9le -----------------------------------
gcc/11.2.0  kokkos/4.0.01  
[root@c5ad0d45ba1d /]# module load gcc
[root@c5ad0d45ba1d /]# module load kokkos
```
