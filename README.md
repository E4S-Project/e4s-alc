# E4S à la Carte

## Description

E4S à la Carte is a practical tool designed to facilitate the generation of Dockerfiles infused with OS packages, Spack packages, as well as custom commands. In the simplifying the process, this tool targets the elimination of manual Dockerfile scripting, enabling users to concentrate on critical aspects such as application-specific resources and configurations. 

## Documentation
[![Documentation Status](https://readthedocs.org/projects/e4s-alc/badge/?version=latest)](https://e4s-alc.readthedocs.io/en/latest/?badge=latest)

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

#### Example YAML file with matrix feature

Here is an example `.yaml` file that creates multiple Dockerfiles using a single `.yaml` file. Notice that for each `registry-image-matrix` item that we specify, we build out a Dockerfile using each `spack-compiler-matrix` item. This feature could be powerful for testing Spack packages across different operating systems and compilers.

```
backend: podman
registry-image-matrix:
  - registry.access.redhat.com/ubi8/ubi
  - ubuntu:20.04

####### Spack group #######
spack: True
spack-version: latest

spack-compiler-matrix:
  - gcc@8.5.0 
  - gcc@11.2.0 
  - gcc@12.0
  - gcc@12.3.0

spack-packages: 
  - kokkos
```

This `.yaml` file would create a directory named `dockerfiles` that contains the following Dockerfiles:
```
Dockerfile.rhel8.8-gcc@8.5.0
Dockerfile.rhel8.8-gcc@11.5.0
Dockerfile.rhel8.8-gcc@12.0
Dockerfile.rhel8.8-gcc@12.3.0
Dockerfile.ubuntu20.04-gcc@8.5.0
Dockerfile.ubuntu20.04-gcc@11.5.0
Dockerfile.ubuntu20.04-gcc@12.0
Dockerfile.ubuntu20.04-gcc@12.3.0
```
