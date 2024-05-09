from e4s_alc.model.model import Model
from e4s_alc.model.create_dockerfile import CreateDockerfileModel
from e4s_alc.model.create_definitionfile import CreateDefinitionfileModel

modules_content = """modules:
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
