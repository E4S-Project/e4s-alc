RM = rm -f
MV = mv -f
COPY = cp -rv
MKDIR = mkdir -p
RMDIR = rm -fr

VERSION = $(shell git describe --tags --abbrev=0 2>/dev/null || echo "0.0.1")

# Get build system locations from configuration file or command line
ifneq ("$(wildcard setup.cfg)","")
	PREFIX = $(shell grep '^prefix =' setup.cfg | sed 's/prefix = //')
endif
ifeq ($(PREFIX),)
	PREFIX=$(shell pwd)/e4s-alc-$(VERSION)
endif
INSTALL_BIN_DIR=$(PREFIX)/bin

# Get target OS and architecture
ifeq ($(HOST_OS),)
	HOST_OS = $(shell uname -s)
endif
ifeq ($(HOST_ARCH),)
	HOST_ARCH = $(shell uname -m)
endif

WGET = $(shell command -pv wget || which wget)
CURL = $(shell command -pv curl || which curl)

ifneq ($(WGET),)
download = $(WGET) --no-check-certificate $(WGET_FLAGS) -O "$(2)" "$(1)"
else
ifneq ($(CURL),)
download = $(CURL) --insecure $(CURL_FLAGS) -L "$(1)" > "$(2)"
else
$(error Either curl or wget must be in PATH to download the python interpreter)
endif
endif

# Miniconda configuration
USE_MINICONDA = true
ifeq ($(HOST_OS),Linux)
	CONDA_OS = Linux
else
	USE_MINICONDA = false
endif
ifeq ($(HOST_ARCH),x86_64)
	CONDA_ARCH = x86_64
else
	ifeq ($(HOST_ARCH),ppc64le)
	CONDA_ARCH = ppc64le
else
	USE_MINICONDA = false
endif
endif

CONDA_VERSION = latest
CONDA_REPO = https://repo.anaconda.com/miniconda
CONDA_PKG = Miniconda3-$(CONDA_VERSION)-$(CONDA_OS)-$(CONDA_ARCH).sh
CONDA_URL = $(CONDA_REPO)/$(CONDA_PKG)
CONDA_SRC = system/src/$(CONDA_PKG)
CONDA_DEST = $(PREFIX)/conda
CONDA_BIN = $(CONDA_DEST)/bin
CONDA = $(CONDA_DEST)/bin/python

ifeq ($(USE_MINICONDA),true)
	PYTHON_EXE = $(CONDA)
	PYTHON_FLAGS = -EOu
else
	$(warning WARNING: There are no miniconda packages for this system: $(HOST_OS), $(HOST_ARCH).)
	CONDA_SRC =
	PYTHON_EXE = $(shell command -pv python || type -P python || which python)
	PYTHON_FLAGS = -O
	ifeq ($(PYTHON_EXE),)
		$(error python not found in PATH.)
	else
		$(warning WARNING: Trying to use '$(PYTHON_EXE)' instead.)
	endif
endif
PYTHON = $(PYTHON_EXE) $(PYTHON_FLAGS)

all: install

#>============================================================================<
# Conda setup and fetch target

$(CONDA): $(CONDA_SRC)
	bash $< -b -p $(CONDA_DEST)
	touch $(CONDA_BIN)/*

$(CONDA_SRC):
	$(MKDIR) `dirname "$(CONDA_SRC)"`
	$(call download,$(CONDA_URL),$(CONDA_SRC)) || \
		(rm -f "$(CONDA_SRC)" ; \
		echo "* ERROR: Unable to download $(CONDA_URL)." ; \
		false)

#>============================================================================<
# Main installation target

install: $(PYTHON_EXE)
	$(PYTHON) -m pip install -q --compile .
	$(MKDIR) $(INSTALL_BIN_DIR)
	ln -fs $(CONDA_BIN)/e4s-alc $(INSTALL_BIN_DIR)/e4s-alc

install-dev: $(PYTHON_EXE)
	$(PYTHON) -m pip install -q --editable .
	$(MKDIR) $(INSTALL_BIN_DIR)
	ln -fs $(CONDA_BIN)/e4s-alc $(INSTALL_BIN_DIR)/e4s-alc
