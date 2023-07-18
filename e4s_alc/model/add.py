from e4s_alc.mvc.model import Model
from e4s_alc.model.container import *
from e4s_alc import logger

LOGGER = logger.get_logger(__name__)

class AddModel(Model):
    def __init__(self):
        super().__init__(module_name='AddModel')

    def main(self, args):
        args.spack = False
        if not self.backend:
            LOGGER.info('No backend set. Run \'e4s-alc init\'.')
            exit(1)

        if self.backend not in SUPPORTED_BACKENDS:
            LOGGER.info('Backend \'{}\' not supported.'.format(self.backend))
            exit(1)

        if not self.check_working_backend(self.backend, SUPPORTED_BACKENDS[self.backend]):
            LOGGER.info('Failed to connect to \'{}\' client'.format(self.backend))
            exit(1)

        if args.file:
            file_args = self.controller.read_args_file(args.file)
            if 'name' not in file_args:
                LOGGER.info('Input file must include a name')
                exit(1)
            args.name = file_args['name']

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
                    LOGGER.info('Invalid copy format. Use {host-path}:{image-path}')
                    exit(1)
                host_image_path = item.split(':')
                if len(host_image_path) != 2:
                    LOGGER.info('Invalid copy format. Use {host-path}:{image-path}')
                    exit(1)
                host_path, image_path = host_image_path
                self.controller.mount_and_copy(host_path, image_path)

        if self.backend == "singularity" and args.parent:
            self.controller.set_parent(args.parent)

        self.controller.read_image(args.name)
        self.controller.add_system_package_commands(args.os_package)

        if args.tarball:
            for item in args.tarball:
                if ':' not in item:
                    LOGGER.info('Invalid tarball format. Use {host-tarball-path/tarball-url}:{image-tarball-path}')
                    exit(1)

                if item.startswith('http'):
                    item_split = item.split(':')
                    url_path = ':'.join(item_split[:2])
                    image_path = item_split[2]
                    self.controller.expand_tarball(url_path, image_path)

                else:
                    host_image_path = item.split(':')
                    if len(host_image_path) != 2:
                        LOGGER.info('Invalid tarball format. Use {host-tarball-path}:{image-tarball-path}')
                        exit(1)
                    host_path, image_path = host_image_path
                    self.controller.expand_tarball(host_path, image_path)

        if args.spack:
            self.controller.install_spack()

        if args.yaml:
            self.controller.spack_yaml_configuration(args.yaml)

        if args.package:
            if args.spack==False:
                self.controller.install_spack()
            self.controller.add_spack_package_commands(args.package)

        self.controller.execute_build(args.name)
