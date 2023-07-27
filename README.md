# E4S à la Carte

## Description

E4S à la Carte is a practical tool designed to facilitate the generation of Dockerfiles infused with OS packages, Spack packages, as well as custom commands. In the simplifying the process, this tool targets the elimination of manual Dockerfile scripting, enabling users to concentrate on critical aspects such as application-specific resources and configurations. 

## Table of Contents

- [Overview](##Overview)
- [Installation](#Installation)
- [Usage](#Usage)
- [Crafting a YAML file](#Crafting-a-YAML-file)
    - [The Base Group](#The-Base-Group)
    - [The System Group](#The-System-Group)
    - [The Spack Group](#The-Spack-Group)
    - [Template](#Template)
    - [Example YAML file](#Example-YAML-file)

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
cd e4s-alc && make
```

## Usage

`e4s-alc` has 3 basic commands:
* `create` - Used to create a Dockerfile
* `build` - Used to create and build a Dockerfile
* `template` - Used to generate a template `.yaml` file

While you are able to use `e4s-alc create` and `e4s-alc build` as a command line tool, it is recommended that you use a `.yaml` file.

To create a Dockerfile, run:
```
e4s-alc create -f example.yaml
```

This will place a Dockerfile and `conf` directory in the current working directory. Do not remove the `conf` directory because this plays a role in the build of the container.

To create a Docker and immediately begin building the container, run:
```
e4s-alc build -f example.yaml
```

This is the same as running `e4s-alc create -f example.yaml && {docker/podman} build .`

To create a template `.yaml` file to work off, run:
```
e4s-alc template
```

This will print a template `.yaml` file using `e4s-alc` syntax.

### Crafting a YAML file

The `.yaml` file, which serves as the input, is segmented into three categories: 
* Base group
* System group
* Spack group

Each of these groups manages resource allocation, variables, executables, files, and packages related to their group.

--------
#### The Base Group

Parameters of the base group define the setup of the image and consist of the following: 
* `backend` - Represents the container backend utilized to obtain and analyze image particulars for further configurations. Docker and Podman are examples of backends.
* `registry` - Specifies the registry that hosts the fundamental image you're building on.
* `image` - Represents the name of the base image sourced from the `registry`.
* `initial-commands` - A set of commands that execute at the commencement of the Dockerfile build.
* `env-variables` - Defines environment variables that are set within the Dockerfile. 
* `add-files` - Specifies the local files to be added in the image.
* `post-base-stage-commands` - Includes a set of commands executed at the end of the Base Stage of the Dockerfile build.

--------
#### The System Group

The system group gathers crucial binaries required for Spack as well as user-specific projects.
* `pre-system-stage-commands` - A set of commands executed at the start of the System Stage of the Dockerfile build.
* `os-packages` - A set of OS packages to be included in the image. Note: `e4s-alc` auto-includes some OS packages for Spack's usability.
* `certificates` - Includes `.pem`/`.cer` certificates required by your organization to download OS packages and for added security purposes.
* `add-repos` - A set of GitHub repositories to be cloned into the image.
* `post-system-stage-commands` - A set of commands executed at the end of the System Stage of the Dockerfile build.

--------
#### The Spack Group

Spack group parameters deal with Spack installation and package inclusion for your image.
* `spack` - A boolean to decide if Spack should be included in the image. If set to `False`, the Spack Stage is bypassed. Default is `True`.
* `pre-spack-stage-commands` - A set of commands that execute at the start of the Spack Stage of the Dockerfile build.
* `spack-version` - Specifies the version of Spack to install in the `X.Y.Z` format representing major, minor, and point release versions. Default is the latest Spack version.
* `spack-mirrors` - A set of Spack mirrors that will be used to build Spack packages.
* `spack-check-signatures` - A boolean to decide if Spack should check for signatures when installing Spack packages. Default is `True`.
* `modules-env-file` - The local `modules.yaml` file used to configure environment modules.
* `post-spack-install-commands` - A set of commands that execute after Spack installation.
* `spack-env-file` - The local `spack.yaml` file used to build out Spack environments.
* `spack-compiler` - The Spack compiler to be installed for building the specified Spack packages.
* `spack-packages` - A set of Spack packages to be installed into the image.
* `post-spack-stage-commands` - A set of commands that execute towards the end of the Spack Stage of the Dockerfile build.

--------
#### Template

A template `.yaml` can be generated with the command:
```
e4s-alc template
```

The template is also described here:

<details>
  <summary>Template</summary>

   ```
   ######## Base group ########
   backend:
   registry:
   image:
   
   initial-commands:
     -
   
   env-variables: 
     -
   
   add-files: 
     -
   
   post-base-stage-commands:
     -
   
   ######## System group ########
   pre-system-stage-commands: 
     -
   
   certificates:
     -
   
   os-packages: 
     -
   
   post-system-stage-commands: 
     -
   
   ####### Spack group #######
   spack: True
   
   pre-spack-stage-commands:
     -
   
   spack-version:
   spack-mirrors:
     -

   spack-check-signature: True
   modules-env-file:
   post-spack-install-commands: 
     -
   
   spack-env-file:
   spack-compiler:
   spack-packages: 
     -
   
   post-spack-stage-commands: 
     -
   ```
</details>

--------
#### Example YAML file

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

or

```
e4s-alc build -f rhel8-gcc11.2-kokkos.yaml
```

Then, I run the image in interactive mode and inspect the install:

```
[root@c5ad0d45ba1d /]# module avail
----------------------------- /modulefiles/linux-rhel8-power9le -----------------------------------
gcc/11.2.0  kokkos/4.0.01  
[root@c5ad0d45ba1d /]# module load gcc
[root@c5ad0d45ba1d /]# module load kokkos
```
