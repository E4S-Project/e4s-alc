import os
import yaml
import time
import tempfile
import argparse
from itertools import product
from e4s_alc.model.create import CreateModel
from e4s_alc.util import Logger, YAMLNotFoundError
from e4s_alc.cli.cli_view import HelpDescriptionFormatter
from e4s_alc.cli.commands.command import AbstractCommand

class CreateCommand(AbstractCommand):
    """A class represents the Create Command, used to create a Dockerfile."""

    def __init__(self):
        """Initialize the CreateCommand class."""
        
        self.parser = None
        self.usage = 'e4s-alc create [options]'
        self.help = 'Create a Dockerfile'

    def create_subparser(self, subparsers):
        """Create subparser and its attributes for this command."""

        self.parser = subparsers.add_parser('create',
                                            help=self.help,
                                            usage=self.usage,
                                            add_help=False,
                                            formatter_class=HelpDescriptionFormatter
                                            )


        self.parser.add_argument('-h', '--help', help='Display the help page', default=False, action='store_true', dest='help')
        self.parser.add_argument('-v', '--verbose', help='Verbose mode', default=False, action='store_true', dest='verbose')
        self.parser.add_argument('-n', '--name', help='Name of the output file')

        file_group_args = self.parser.add_argument_group('Load Arguments by file')
        file_group_args.add_argument('-f', '--file', help='The file used to create a new image')
        
        base_group_desc = 'The base stage of the Dockerfile provides the foundation of the image.'
        base_group_args = self.parser.add_argument_group('Base Stage Arguments', base_group_desc)
        base_group_args.add_argument('-b', '--backend', help='The container backend used for image inspection. Available backends are Docker, Podman and Singularity')
        base_group_args.add_argument('-i', '--image', help='The base image name <image:tag>')
        base_group_args.add_argument('-r', '--registry', help='The image registry to search for the base image')
        base_group_args.add_argument('--env-variable', help='Set an environment variable inside the container', action='append', default=[], dest='env-variables')
        base_group_args.add_argument('--add-file', help='Add a file to the container', action='append', default=[], dest='add-files')
        base_group_args.add_argument('--initial-command', help='Commands to run after image is pulled', action='append', default=[], dest='initial-commands')
        base_group_args.add_argument('--post-base-stage-command', help='Commands to run at the end of the base stage', action='append', default=[], dest='post-base-stage-commands')

        system_group_desc = 'The system stage of the Dockerfile provides important dependencies that the image might need.'
        system_group_args = self.parser.add_argument_group('System Stage Arguments', system_group_desc)
        system_group_args.add_argument('-crt', '--certificate', help='Add an SSL certificate', action='append', default=[], dest='certificates')
        system_group_args.add_argument('-a', '--os-package', help='The name of an OS Package to install', action='append', default=[], dest='os-packages')
        system_group_args.add_argument('--add-remote-file', help='Add a remote file to the container', action='append', default=[], dest='add-remote-files')
        system_group_args.add_argument('--add-repo', help='Clone a GitHub repository into the image', action='append', default=[], dest='add-repos')
        system_group_args.add_argument('--pre-system-stage-command', help='Commands to run at the beginning of the system stage', action='append', default=[], dest='pre-system-package-commands')
        system_group_args.add_argument('--post-system-stage-command',  help='Commands to run at the end of the system stage', action='append', default=[], dest='post-system-package-commands')

        spack_group_desc = 'The Spack stage of the Dockerfile provides Spack installations for the image.'
        spack_group_args = self.parser.add_argument_group('Spack Stage Arguments', spack_group_desc)
        spack_group_args.add_argument('-s', '--spack', help='Choose to install spack', default=True, dest='spack')
        spack_group_args.add_argument('--spack-version', help='The version of a Spack to install', dest='spack-version')
        spack_group_args.add_argument('--spack-mirrors', help='The Spack mirror URL/Paths for Spack package caches.', default=[], dest='spack-mirrors')
        spack_group_args.add_argument('--spack-check-signature', help='Check for Spack package signature when installing packages from mirror', default=True, dest='spack-check-signature')
        spack_group_args.add_argument('--modules-yaml-file', help='The path to a modules.yaml environment file', dest='modules-yaml-file')
        spack_group_args.add_argument('--spack-compiler', help='The Spack compiler that will be installed and will build Spack packages', dest='spack-compiler')
        spack_group_args.add_argument('--spack-yaml-file', help='The path to a spack.yaml environment file', dest='spack-yaml-file')
        spack_group_args.add_argument('-p', '--spack-package', help='The name of a Spack package to install', action='append', default=[], dest='spack-packages')
        spack_group_args.add_argument('--pre-spack-stage-command', help='Commands to run at the beginning of the spack stage', action='append', default=[], dest='pre-spack-install-commands')
        spack_group_args.add_argument('--post-spack-install-command', help='Commands to run after Spack is installed', action='append', default=[], dest='post-spack-install-commands')
        spack_group_args.add_argument('--post-spack-stage-command', help='Commands to run at the end of the spack stage', action='append', default=[], dest='post-spack-package-commands')

        matrix_option_desc = 'The matrix options allow users to build multiple Dockerfiles in one call with.'
        matrix_option_args = self.parser.add_argument_group('Matrix Option Arguments', matrix_option_desc)
        matrix_option_args.add_argument('--registry-image-matrix', help='The registry+image paths for each image to build', action='append', default=[], dest='registry-image-matrix')
        matrix_option_args.add_argument('--spack-version-matrix', help='The Spack version for each image to build', action='append', default=[], dest='spack-version-matrix')
        matrix_option_args.add_argument('--spack-compiler-matrix', help='The Spack compiler for each image to build', action='append', default=[], dest='spack-compiler-matrix')

        return {'command': self, 'parser': self.parser}

    def check_arguments(self, args):
        """Check the arguments passed to the command."""

        timestamp = int(time.time())
        log_dir = tempfile.mkdtemp(prefix=f'e4s-alc-{timestamp}-')
        log_path = os.path.join(log_dir, 'logs.log')
        logger = Logger('core', log_path, args['verbose'])

        print(f"Logs will be saved to {log_path}")
        
        if args['help']:
            self.parser.print_help()
            exit(0)

        if not (args['image'] or args['file']):
            print('Error: Arguments \'-i/--image\' or \'-f/--file\' are required.')
            self.parser.print_help()
            exit(1)

        if args['image'] and args['file']:
            print('Error: Argument \'-f/--file\' cannot be used with argument \'-i/--image\'.')
            self.parser.print_help()
            exit(1)

    def read_arguments_from_file(self, file_path):
        abs_file_path = os.path.abspath(file_path)

        if not os.path.isfile(abs_file_path):
            raise YAMLNotFoundError(abs_file_path)

        with open(abs_file_path, 'r') as file:
            if file_path.endswith('.yaml'):
                data = yaml.safe_load(file)
                data['file'] = None
            else:
                print('Invalid file format. Please provide .yaml file format. Run `e4s-alc template` to generate a template .yaml file.')
                exit(1)
        return data

    def create_model(self, args):
        self.check_arguments(args)
        model = CreateModel(args)
        model.create()

    def generate_combinations(self, args, matrices):
        # Filter out empty lists
        matrices = {k: v for k, v in matrices.items() if v}

        # Generate a product of items in the dictionary and create a model
        for values in product(*matrices.values()):
            data = dict(zip(matrices.keys(), values))
            args = {**args, 'matrix': True, **data}
            self.create_model(args)

    def run(self, arg_namespace):
        """Run the command after checking the arguments."""
        args = vars(arg_namespace)

        # Check if a file with arguments exists and load its content into 'args'.
        if args['file']:
            file_args = self.read_arguments_from_file(args['file'])
            args = {**args, **file_args, 'matrix': False}

        # Extract command matrices for registry images and spack compilers.
        matrices = {
            "image": args.get('registry-image-matrix', []),
            "spack-version": args.get('spack-version-matrix', []),
            "spack-compiler": args.get('spack-compiler-matrix', [])
        }

        if matrices['image'] or matrices['spack-version'] or matrices['spack-compiler']:
            self.generate_combinations(args, matrices)
            return


        # If no matrices, check, create and execute the model with the original arguments.
        self.check_arguments(args)
        model = CreateModel(args)
        model.create()
