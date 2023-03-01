from e4s_alc.mvc.model import Model
from e4s_alc.model.container import *

class CreateModel(Model):
    def __init__(self):
        super().__init__(module_name='CreateModel')

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


        #TODO Add functionality for file read in

        if args.copy:
            for item in args.copy:
                if ':' not in item:
                    print('Invalid copy format. Use {host-path}:{image-path}')
                    exit(1)
                host_image_path = item.split(':')
                if len(host_image_path) != 2:
                    print('Invalid copy format. Use {host-path}:{image-path}')
                    exit(1)
                host_path, image_path = host_image_path
                self.controller.mount_and_copy(host_path, image_path)

        self.controller.init_image(args.image)
        self.controller.add_system_package_commands(args.os_package)
        self.controller.install_spack()
        self.controller.add_spack_package_commands(args.package)
        self.controller.execute_build(args.name)
