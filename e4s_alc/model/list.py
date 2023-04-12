from e4s_alc.mvc.model import Model
from e4s_alc.model.container import *

class ListModel(Model):
    def __init__(self):
        super().__init__(module_name='ListModel')

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

        self.controller.list_images(args.name, args.inter)
