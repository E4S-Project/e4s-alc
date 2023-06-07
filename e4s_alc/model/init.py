from e4s_alc.mvc.model import Model
from e4s_alc.model.container import * 
from e4s_alc import logger

LOGGER = logger.get_logger(__name__)

class InitModel(Model):
    def __init__(self):
        super().__init__(module_name='InitModel')

    def discover_backend(self):
        # Check for container runtime
        for backend, controller in SUPPORTED_BACKENDS.items():
            if self.check_working_backend(backend, controller):
                LOGGER.warning('Found {}!'.format(backend))
                self.set_backend(backend)
                return True
        return False


    def main(self, args):
        if args.backend:
            if args.backend not in SUPPORTED_BACKENDS:
                print('Error: backend \'{}\' not supported'.format(args.backend))
                exit(1)

            elif not self.check_working_backend(args.backend, SUPPORTED_BACKENDS[args.backend]):
                print('Error: failed to find backend: {}'.format(args.backend))
                exit(1)
            else:
                self.set_backend(args.backend)
                print('Found {}!'.format(args.backend))

        else:
            if not self.discover_backend():
                print('Error: No backend discovered')
                exit(1)
