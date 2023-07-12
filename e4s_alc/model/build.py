import logging
from e4s_alc.model.create import CreateModel

logger = logging.getLogger('core')

class BuildModel(CreateModel):
    def __init__(self, arg_namespace):
        logger.info('Initializing BuildModel')
        super().__init__(arg_namespace=arg_namespace)

    def build(self):
        logger.info('Creating and building the container')
        self.create()
        self.controller.build()                
