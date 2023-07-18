from e4s_alc.mvc.model import Model
from e4s_alc.model.container import *
from e4s_alc import logger

LOGGER = logger.get_logger(__name__)

class DeleteModel(Model):
    def __init__(self):
        super().__init__(module_name='DeleteModel')

    def main(self, args):
        if not self.backend:
            LOGGER.info('No backend set. Run \'e4s-alc init\'.')
            exit(1)

        if self.backend not in SUPPORTED_BACKENDS:
            LOGGER.info('Backend \'{}\' not supported.'.format(self.backend))
            exit(1)

        if not self.check_working_backend(self.backend, SUPPORTED_BACKENDS[self.backend]):
            LOGGER.info('Failed to connect to \'{}\' client'.format(self.backend))
            exit(1)

        if args.prune_containers:
            self.controller.prune_containers()
        if args.prune_images:
            self.controller.prune_images()
        if args.container:
            self.controller.delete_container(args.container, args.force)
        if args.name:
            self.controller.delete_image(args.name, args.force)
        if args.id:
            self.controller.delete_image(args.id, args.force)
