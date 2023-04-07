Operating Systems supported: 

- ![](https://raw.githubusercontent.com/EgoistDeveloper/operating-system-logos/master/src/24x24/UBT.png "Ubuntu (16x16)") Ubuntu ✅ 
- ![](https://raw.githubusercontent.com/EgoistDeveloper/operating-system-logos/master/src/24x24/RHT.png "Red Hat (16x16)") Red Hat ✅
- ![](https://raw.githubusercontent.com/EgoistDeveloper/operating-system-logos/master/src/24x24/SSE.png "Suse (48x48)") SUSE ✅

Backends supported:

- <img src="https://www.docker.com/wp-content/uploads/2022/03/horizontal-logo-monochromatic-white.png" width="100" height="30"> Docker ✅
- <img src="https://github.com/containers/podman/raw/main/logo/podman-logo-source.svg" width="100" height="30"> Podman (In progress)


# E4S-ALC

Build docker images quickly with Spack integration.

### Install

```
$ pip3 install e4s-alc
```

### Usage

Initialize the backend

```
$ e4s-alc init
```

Create image

```
$ e4s-alc create \
	--image centos:8 \
	--name my-centos-image \
	-p py-numpy \
	-p autodiff
```
or
```
$ e4s-alc create \
	--image ubuntu:22.04 \
	--name my-ubuntu-image \
	--no-spack
```
or
```
$ cat test.json

{
	"image": "ubuntu:22.04",
	"name": "test-file-kokkos-raja",
	"spack": true,
	"spack-packages": [
		"kokkos",
		"raja"
	],
	"os-packages": [
		"neovim",
		"valgrind"
	]
}

$ e4s-alc create -f test.json
```

Add package to image

```
$ e4s-alc add -n my-ubuntu-image -p kokkos -a neovim
```

### Examples

Create an E4S image loaded with intel oneapi compilers and create a centos:8 image loaded with kokkos in a single call:
```
$ e4s-alc create \
	--image ecpe4s/ubuntu20.04-runner-x86_64:2022-12-01 \
	--name e4s-intel \
	-p intel-oneapi-compilers \ 
&& \
e4s-alc create \
	--image centos:8 \
	--name centos8-kokkos \
	-p kokkos 
```
