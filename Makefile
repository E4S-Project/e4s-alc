VERSION := $(shell git describe --tags --abbrev=0 2>/dev/null || echo "0.0.1")
PREFIX := $(shell pwd)/e4s-alc-$(VERSION)
INSTALL_BIN_DIR := $(PREFIX)/bin
HOST_OS := $(or $(HOST_OS), $(shell uname -s))
HOST_ARCH := $(or $(HOST_ARCH), $(shell uname -m))

DL_CMD := $(if $(shell command -pv wget || which wget), $(shell command -pv wget || which wget) --no-check-certificate -O, $(if $(shell command -pv curl || which curl), $(shell command -pv curl || which curl) --insecure -L, $(error Either curl or wget must be in PATH)))

USE_MINICONDA := true
ifdef HOST_OS
ifneq ($(HOST_OS),Linux)
    USE_MINICONDA := false
endif
endif
CONDA_ARCH := $(or $(filter $(HOST_ARCH), x86_64 ppc64le aarch64), $(USE_MINICONDA := false))
CONDA_VERSION := latest
CONDA_REPO := https://repo.anaconda.com/miniconda
CONDA_PKG := Miniconda3-$(CONDA_VERSION)-$(HOST_OS)-$(CONDA_ARCH).sh
CONDA_URL := $(CONDA_REPO)/$(CONDA_PKG)
CONDA_SRC := system/src/$(CONDA_PKG)
CONDA_DEST := $(PREFIX)/conda
CONDA_BIN := $(CONDA_DEST)/bin
CONDA := $(CONDA_DEST)/bin/python

ifeq ($(USE_MINICONDA),true)
	PYTHON_EXE := $(CONDA)
	PYTHON_FLAGS := -EOu
else
    $(warning WARNING: There are no miniconda packages for this system $(HOST_OS) $(HOST_ARCH) - $(CONDA_URL))
	CONDA_SRC :=
	PYTHON_EXE := $(shell command -pv python || type -P python || which python)
	PYTHON_FLAGS := -O
	ifeq ($(PYTHON_EXE),)
		$(error python not found in PATH.)
	else
		$(warning WARNING:  Trying to use '$(PYTHON_EXE)' instead.)
	endif
endif
PYTHON := $(PYTHON_EXE) $(PYTHON_FLAGS)

all: install

$(CONDA): $(CONDA_SRC)
	bash $< -b -p $(CONDA_DEST)
	touch $@

$(CONDA_SRC):
	mkdir -p $(@D)
	$(DL_CMD) $(CONDA_URL) $@

install: $(PYTHON_EXE)
	$(PYTHON) -m pip install -q --compile .
	mkdir -p $(INSTALL_BIN_DIR)
	ln -fs $(CONDA_BIN)/e4s-alc $(INSTALL_BIN_DIR)/e4s-alc

install-dev: install
	$(PYTHON) -m pip install -q --editable .
