import os
import sys
import shutil
import logging
from e4s_alc.model import CreateDockerfileModel, CreateDefinitionfileModel, Model
from urllib.parse import urlparse
from e4s_alc.model import Model, modules_content
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
        with open(MODULES_YAML, "w") as f:
            f.write(modules_content)
