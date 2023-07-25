from e4s_alc.util import Logger
from e4s_alc.model.create import CreateModel
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

        file_group_args = self.parser.add_argument_group('Load Arguments by file')
        file_group_args.add_argument('-f', '--file', help='The file used to create a new image')
        
        base_group_desc = 'The base stage of the Dockerfile provides the foundation of the image.'
        base_group_args = self.parser.add_argument_group('Base Stage Arguments', base_group_desc)
        base_group_args.add_argument('-b', '--backend', help='The container backend used for image inspection')
        base_group_args.add_argument('-i', '--image', help='The base image name <image:tag>')
        base_group_args.add_argument('-r', '--registry', help='The image registry to search for the base image')
        base_group_args.add_argument('-ev', '--env-variable', help='Set an environment variable inside the container', action='append', default=[], dest='env-variables')
        base_group_args.add_argument('-af', '--add-file', help='Add a file to the container', action='append', default=[], dest='add-files')
        base_group_args.add_argument('--initial-command', help='Commands to run after image is pulled', action='append', default=[], dest='initial-commands')
        base_group_args.add_argument('--post-base-stage-command', help='Commands to run at the end of the base stage', action='append', default=[], dest='post-base-stage-commands')

        system_group_desc = 'The system stage of the Dockerfile provides important dependencies that the image might need.'
        system_group_args = self.parser.add_argument_group('System Stage Arguments', system_group_desc)
        system_group_args.add_argument('-crt', '--certificate', help='Add an SSL certificate', action='append', default=[], dest='certificates')
        system_group_args.add_argument('-a', '--os-package', help='The name of an OS Package to install', action='append', default=[], dest='os-packages')
        system_group_args.add_argument('--pre-system-stage-command', help='Commands to run at the beginning of the system stage', action='append', default=[], dest='pre-system-package-commands')
        system_group_args.add_argument('--post-system-stage-command',  help='Commands to run at the end of the system stage', action='append', default=[], dest='post-system-package-commands')

        spack_group_desc = 'The Spack stage of the Dockerfile provides Spack installations for the image.'
        spack_group_args = self.parser.add_argument_group('Spack Stage Arguments', spack_group_desc)
        spack_group_args.add_argument('-s', '--spack', help='Choose to install spack', default=True, dest='spack')
        spack_group_args.add_argument('-sv', '--spack-version', help='The version of a Spack to install')
        spack_group_args.add_argument('-sm', '--spack-mirrors', help='The Spack mirror URL/Paths for Spack package caches.', default=[], dest='spack-mirrors')
        spack_group_args.add_argument('-ss', '--spack-check-signature', help='Check for Spack package signature when installing packages from mirror', default=True)
        spack_group_args.add_argument('-me', '--modules-env-file', help='The path to a modules.yaml environment file')
        spack_group_args.add_argument('-sc', '--spack-compiler', help='The Spack compiler that will be installed and will build Spack packages')
        spack_group_args.add_argument('-se', '--spack-env-file', help='The path to a spack.yaml environment file')
        spack_group_args.add_argument('-p', '--spack-package', help='The name of a Spack package to install', action='append', default=[], dest='spack-packages')
        spack_group_args.add_argument('--pre-spack-stage-command', help='Commands to run at the beginning of the spack stage', action='append', default=[], dest='pre-spack-install-commands')
        spack_group_args.add_argument('--post-spack-install-command', help='Commands to run after Spack is installed', action='append', default=[], dest='post-spack-install-commands')
        spack_group_args.add_argument('--post-spack-stage-command', help='Commands to run at the end of the spack stage', action='append', default=[], dest='post-spack-package-commands')

        return {'command': self, 'parser': self.parser}

    def check_arguments(self, arg_namespace):
        """Check the arguments passed to the command."""

        logger = Logger('core', '.logs.log', arg_namespace.verbose)

        if arg_namespace.help:
            self.parser.print_help()
            exit(0)

        if not (arg_namespace.image or arg_namespace.file):
            print('Error: Arguments \'-i/--image\' or \'-f/--file\' are required.')
            self.parser.print_help()
            exit(1)

        if arg_namespace.image and arg_namespace.file:
            print('Error: Argument \'-f/--file\' cannot be used with argument \'-i/--image\'.')
            self.parser.print_help()
            exit(1)

    def run(self, arg_namespace):
        """Run the command after checking the arguments."""
        
        self.check_arguments(arg_namespace)
        model = CreateModel(arg_namespace)
        model.create()
