import os
import sys
import shutil
import logging
from e4s_alc.model import CreateDockerfileModel, CreateDefinitionfileModel, Model
from urllib.parse import urlparse
from e4s_alc.model import Model
from e4s_alc.util import log_function_call

logger = logging.getLogger('core')

MODULES_YAML = os.path.expanduser("~") + "/.e4s-alc/modules-template.yaml"

class CreateModel(Model):
    @log_function_call
    def __init__(self, arg_namespace):
        super().__init__(module_name=self.__class__.__name__, arg_namespace=arg_namespace)

        # Check if the modules_yaml file exists
        if not os.path.isfile(MODULES_YAML):
            self.write_modules_yaml()

        if self.backend == "singularity":
            self.BackendModel = CreateDefinitionfileModel(arg_namespace)
        else:
            self.BackendModel = CreateDockerfileModel(arg_namespace)

    def create(self):
        self.BackendModel.create()

    def write_modules_yaml(self):
        modules_content = """
modules:
  prefix_inspections:
    ./bin:
      - PATH
    ./lib:
    - LIBRARY_PATH
    - LD_LIBRARY_PATH
    ./lib64:
    - LIBRARY_PATH
    - LD_LIBRARY_PATH
    ./include:
    - INCLUDE
    ./man:
    - MANPATH
    ./share/man:
    - MANPATH
    ./share/aclocal:
    - ACLOCAL_PATH
    ./lib/pkgconfig:
    - PKG_CONFIG_PATH
    ./lib64/pkgconfig:
    - PKG_CONFIG_PATH
    ./share/pkgconfig:
    - PKG_CONFIG_PATH
    ./:
    - CMAKE_PREFIX_PATH
  default:
    roots:
     tcl:   /modulefiles
    enable:
      - tcl
    tcl:
      exclude_implicits: true
      hash_length: 0
      projections:
        all: '{name}/{version}'
      all:
        conflict:
        - '{name}'
        environment:
          set:
            '{name}_ROOT': '{prefix}'
            '{name}_VERSION': '{version}'
            '{name}_BIN': '{prefix.bin}'
            '{name}_INC': '{prefix.include}'
            '{name}_LIB': '{prefix.lib}'
        autoload: none
      blas:
        environment:
          set:
            'BLAS_ROOT': '{prefix}'
            'LAPACK_ROOT': '{prefix}'
"""
        with open(MODULES_YAML, "w") as f:
            f.write(modules_content)
