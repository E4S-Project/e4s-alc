This code is unstable. The structure of this project is being rewritten and the original code can be found at https://github.com/PlatinumCD/Boxmake.

# E4S-ALC

Build docker images quickly with Spack integration.

### Install

```
$ pip3 install e4s-alc
```

### Usage

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

List images

```
$ e4s-alc list

E4S-ALC images:
====================
	my-centos-image (centos:8): - 2022-01-01 00:00:00
		+ py-numpy
		+ autodiff

	my-ubuntu-image (ubuntu:22.04): - 2022-01-01 00:00:00
		No spack packages or spack installed

	test-file-kokkos-raja (ubuntu:22.04): - 2022-01-01 00:00:00
		+ kokkos
		+ raja
```

Add package to image

```
$ e4s-alc add -n my-ubuntu-image -p kokkos -a neovim

$ e4s-alc list

E4S-ALC images:
====================
        my-centos-image (centos:8): - 2022-01-01 00:00:00
                + py-numpy
                + autodiff

        my-ubuntu-image (ubuntu:22.04): - 2022-01-01 00:00:00
		+ kokkos

        test-file-kokkos-raja (ubuntu:22.04): - 2022-01-01 00:00:00
                + kokkos
		+ raja

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

$ e4s-alc list

E4S-ALC images:
====================
	cameron-kokkos (centos:8): - 2022-12-31 11:29:49.014343
		+ kokkos

	e4s-intel (ecpe4s/ubuntu20.04-runner-x86_64:2022-12-01): - 2022-12-31 11:35:53.293490
		+ intel-oneapi-compilers
```
