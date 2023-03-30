from e4s_alc.mvc.model import Model
from e4s_alc.model.container import *

class DeleteModel(Model):
    def __init__(self):
        super().__init__(module_name='DeleteModel')

    def main(self, args):
        if not self.backend:
            print('No backend set. Run \'e4s-alc init\'.')
            exit(1)

        if self.backend not in SUPPORTED_BACKENDS:
            print('Backend \'{}\' not supported.'.format(self.backend))
            exit(1)

        if not self.check_working_backend(self.backend, SUPPORTED_BACKENDS[self.backend]):
            print('Failed to connect to \'{}\' client'.format(self.backend))
            exit(1)

        self.controller.delete_image(args.name, args.force)
