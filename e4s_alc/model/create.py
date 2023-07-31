import os
import sys
import shutil
import logging
from e4s_alc.model import CreateDockerfileModel, CreateDefinitionfileModel, Model
from e4s_alc.conf import get_modules_conf

logger = logging.getLogger('core')

class CreateModel(Model):
    def __init__(self, arg_namespace):
        logger.info("Initializing CreateModel")
        super().__init__(module_name=self.__class__.__name__, arg_namespace=arg_namespace)

        if self.backend == "singularity":
            self.BackendModel = CreateDefinitionfileModel(arg_namespace)
        else:
            self.BackendModel = CreateDockerfileModel(arg_namespace)

        self.BackendModel.create()
