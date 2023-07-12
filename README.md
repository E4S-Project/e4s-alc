# E4S à la Carte

## Description

E4S à la Carte is a practical tool designed to facilitate the generation of Dockerfiles infused with OS packages, Spack packages, as well as custom commands. In the simplifying the process, this tool targets the elimination of manual Dockerfile scripting, enabling users to concentrate on critical aspects such as application-specific resources and configurations. 

## Table of Contents

- [Overview](##Overview)
  - [Crafting a YAML file](#Crafting-a-YAML-file)
    - [The Base Group](#The-Base-Group)
    - [The System Group](#The-System-Group)
    - [The Spack Group](#The-Spack-Group)
    - [Template](#Template)
  - [Generated Dockerfile](#Generated-Dockerfile)

## Overview

The `e4s-alc` tool is designed to facilitate the process of crafting Dockerfiles. This tool leverages `.yaml` files as input to generate Dockerfiles.

<a name="desc"></a>
### Crafting a YAML file

The `.yaml` file, which serves as the input, is segmented into three categories: 
* Base group
* System group
* Spack group

Each of these groups manages resource allocation, variables, executables, files, and packages related to their group.

#### The Base Group

Parameters of the base group define the setup of the image and consist of the following: 
* `backend` - Represents the container backend utilized to obtain and analyze image particulars for further configurations. Docker and Podman are examples of backends.
* `registry` - Specifies the registry that hosts the fundamental image you're building on.
* `image` - Represents the name of the base image sourced from the `registry`.
* `initial-commands` - A set of commands that execute at the commencement of the Dockerfile build.
* `env-variables` - Defines environment variables that are set within the Dockerfile. 
* `add-files` - Specifies the local files to be added in the image.
* `post-base-stage-commands` - Includes a set of commands executed at the end of the Base Stage of the Dockerfile build.

#### The System Group

The system group gathers crucial binaries required for Spack as well as user-specific projects.
* `pre-system-stage-commands` - A set of commands executed at the start of the System Stage of the Dockerfile build.
* `certificates` - Includes `.pem`/`.cer` certificates required by your organization to download OS packages and for added security purposes.
* `os-packages` - A set of OS packages to be included in the image. Note: `e4s-alc` auto-includes some OS packages for Spack's usability.
* `post-system-stage-commands` - A set of commands executed at the end of the System Stage of the Dockerfile build.

#### The Spack Group

Spack group parameters deal with Spack installation and package inclusion for your image.
* `spack` - A boolean to decide if Spack should be included in the image. If set to `False`, the Spack Stage is bypassed. Default is `True`.
* `pre-spack-stage-commands` - A set of commands that execute at the start of the Spack Stage of the Dockerfile build.
* `spack-version` - Specifies the version of Spack to install in the `X.Y.Z` format representing major, minor, and point release versions. Default is the latest Spack version.
* `post-spack-install-commands` - A set of commands that execute after Spack installation.
* `spack-env-file` - The local `.yaml` file used to build out Spack environments.
* `spack-packages` - A set of Spack packages to be installed into the image.
* `post-spack-stage-commands` - A set of commands that execute towards the end of the Spack Stage of the Dockerfile build.

#### Template

A template `.yaml` can be generated with the command:
```
e4s-alc template
```

The template is also described here:
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

post-spack-install-commands: 
  -

spack-env-file: 
spack-packages: 
  -

post-spack-stage-commands: 
  -
```

### Generated Dockerfile

The generated Dockerfile consists of 4 stages. The 4 stages are:
* Base Stage
* System Stage
* Spack Stage
* Finalize Stage

#### Base Stage

