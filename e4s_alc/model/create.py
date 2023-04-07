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


        if args.file:
            file_args = self.controller.read_args_file(args.file)
            if 'name' not in file_args:
                print('Input file must include a name')
                exit(1)
            args.name = file_args['name']

            if 'image' not in file_args:
                print('Input file must include an image')
                exit(1)
            args.image = file_args['image']

            if 'spack-packages' in file_args:
                if file_args['spack-packages']:
                    args.package = file_args['spack-packages']

            if 'os-packages' in file_args:
                if file_args['os-packages']:
                    args.os_package = file_args['os-packages']

            if 'copy' in file_args:
                if file_args['copy']:
                    args.copy = file_args['copy']

            if 'tarball' in file_args:
                if file_args['tarball']:
                    args.tarball = file_args['tarball']

            args.spack = True
            if 'spack' in file_args:
                if not file_args['spack']:
                    args.spack = False

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

        if args.tarball:
            for item in args.tarball:
                if ':' not in item:
                    print('Invalid tarball format. Use {host-tarball-path}:{image-tarball-path}')
                    exit(1)
                host_image_path = item.split(':')
                if len(host_image_path) != 2:
                    print('Invalid tarball format. Use {host-tarball-path}:{image-tarball-path}')
                    exit(1)
                host_path, image_path = host_image_path
                self.controller.expand_tarball(host_path, image_path)

        if args.spack:
            self.controller.install_spack()
            self.controller.add_spack_package_commands(args.package)

        self.controller.execute_build(args.name)
