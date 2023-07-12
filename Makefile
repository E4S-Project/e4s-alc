ifneq (,$(findstring v,$(MAKEFLAGS)))
    SILENT =
    CURL_SILENT_FLAG =
    WGET_SILENT_FLAG =
    CONDA_SILENT_FLAG =
else
    SILENT = @
    CURL_SILENT_FLAG = --silent
    WGET_SILENT_FLAG = --quiet
    CONDA_SILENT_FLAG = > /dev/null 

endif

VERSION := $(shell git describe --tags --abbrev=0 2>/dev/null || echo "0.0.1")
PREFIX := $(shell pwd)/e4s-alc-$(VERSION)
INSTALL_BIN_DIR := $(PREFIX)/bin
HOST_OS := $(or $(HOST_OS), $(shell uname -s))
HOST_ARCH := $(or $(HOST_ARCH), $(shell uname -m))

DL_CMD := $(if $(shell command -pv wget || which wget), $(shell command -pv wget || which wget) $(WGET_SILENT_FLAG) --no-check-certificate -O, $(if $(shell command -pv curl || which curl), $(shell command -pv curl || which curl) $(CURL_SILENT_FLAG) --insecure -L, $(error Either curl or wget must be in PATH)))

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
CONDA_SRC := $(PREFIX)/$(CONDA_PKG)
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
	$(SILENT)echo -n "Installing python packages..."
	$(SILENT)bash $< -b -p $(CONDA_DEST) $(CONDA_SILENT_FLAG)
	$(SILENT)touch $@
	$(SILENT)echo "Installing python packages...Complete!"

$(CONDA_SRC):
	$(SILENT)mkdir -p $(@D)
	$(SILENT)echo -n "Downloading Miniconda..."
	$(SILENT) $(DL_CMD) $@ $(CONDA_URL)
	$(SILENT)echo "Complete!"

install: $(PYTHON_EXE)
	$(SILENT)echo -n "Installing e4s-alc through pip..."
	$(SILENT)$(PYTHON) -m pip install -q --compile --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host=files.pythonhosted.org .
	$(SILENT)mkdir -p $(INSTALL_BIN_DIR)
	$(SILENT)ln -fs $(CONDA_BIN)/e4s-alc $(INSTALL_BIN_DIR)/e4s-alc
	$(SILENT)echo "Complete!"
	$(SILENT)echo "Add e4s-alc to your PATH environment variable:"
	$(SILENT)echo
	$(SILENT)echo "Run \`export PATH=\$$(pwd)/e4s-alc-$(VERSION)/bin:\$$PATH\`"
	$(SILENT)echo

install-dev: $(PYTHON_EXE)
	$(SILENT)echo -n "Installing e4s-alc dev through pip..."
	$(SILENT)$(PYTHON) -m pip install -q --editable .
	$(SILENT)mkdir -p $(INSTALL_BIN_DIR)
	$(SILENT)ln -fs $(CONDA_BIN)/e4s-alc $(INSTALL_BIN_DIR)/e4s-alc
	$(SILENT)echo "Complete!"
	$(SILENT)echo "Add e4s-alc to your PATH environment variable:"
	$(SILENT)echo
	$(SILENT)echo "Run \`export PATH=\$$(pwd)/e4s-alc-$(VERSION)/bin:\$$PATH\`"
	$(SILENT)echo

clean:
	$(SILENT)rm -rf $(PREFIX) build e4s_alc.egg-info
