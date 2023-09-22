import os
import sys
import shutil
import logging
from e4s_alc.model import CreateDockerfileModel, CreateDefinitionfileModel, Model
from urllib.parse import urlparse
from e4s_alc.model import Model
from e4s_alc.util import log_function_call

logger = logging.getLogger('core')

class CreateModel(Model):
    @log_function_call
    def __init__(self, arg_namespace):
        super().__init__(module_name=self.__class__.__name__, arg_namespace=arg_namespace)

        if self.backend == "singularity":
            self.BackendModel = CreateDefinitionfileModel(arg_namespace)
        else:
            self.BackendModel = CreateDockerfileModel(arg_namespace)

    def create(self):
        self.BackendModel.create()
