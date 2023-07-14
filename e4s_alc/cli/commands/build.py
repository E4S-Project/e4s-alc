from e4s_alc.model.build import BuildModel
from e4s_alc.cli.cli_view import HelpDescriptionFormatter
from e4s_alc.cli.commands.command import AbstractCommand

class BuildCommand(AbstractCommand):
    """A class representing the Build Command, used to build a container by creating a Dockerfile."""

    def __init__(self):
        """Initialize the BuildCommand class."""

        self.parser = None
        self.usage = 'e4s-alc build [options]'
        self.help = 'Create a Dockerfile and build the container'

    def create_subparser(self, subparsers):
        """Create subparser and its attributes for this command."""

        self.parser = subparsers.add_parser('build',
                                            help=self.help,
                                            usage=self.usage,
                                            add_help=False,
                                            formatter_class=HelpDescriptionFormatter
                                            )


        self.parser.add_argument('-h', '--help', help='Display the help page', default=False, action='store_true', dest='help')
        self.parser.add_argument('-v', '--verbose', help='Verbose mode', default=False, action='store_true', dest='verbose')

        file_group_args = self.parser.add_argument_group('Load Arguments by file')
        file_group_args.add_argument('-f', '--file', metavar='', help='The file used to create a new image')
        
        base_group_desc = 'The base stage of the Dockerfile provides the foundation of the image.'
        base_group_args = self.parser.add_argument_group('Base Stage Arguments', base_group_desc)
        base_group_args.add_argument('-b', '--backend', metavar='', help='The container backend used for image inspection')
        base_group_args.add_argument('-i', '--image', metavar='', help='The base image name <image:tag>')
        base_group_args.add_argument('-r', '--registry', metavar='', help='The image registry to search for the base image')
        base_group_args.add_argument('-ev', '--env-variable', metavar='', help='Set an environment variable inside the container', action='append', default=[], dest='env-variables')
        base_group_args.add_argument('-af', '--add-file', metavar='', help='Add a file to the container', action='append', default=[], dest='add-files')
        base_group_args.add_argument('--initial-command', metavar='', help='Commands to run after image is pulled', action='append', default=[], dest='initial-commands')
        base_group_args.add_argument('--post-base-stage-command', metavar='', help='Commands to run at the end of the base stage', action='append', default=[], dest='post-base-stage-commands')

        system_group_desc = 'The system stage of the Dockerfile provides important dependencies that the image might need.'
        system_group_args = self.parser.add_argument_group('System Stage Arguments', system_group_desc)
        system_group_args.add_argument('-crt', '--certificate', metavar='', help='Add an SSL certificate', action='append', default=[], dest='certificates')
        system_group_args.add_argument('-a', '--os-package', metavar='', help='The name of an OS Package to install', action='append', default=[], dest='os-packages')
        system_group_args.add_argument('--pre-system-stage-command', metavar='', help='Commands to run before OS Packages are installed', action='append', default=[], dest='pre-system-package-commands')
        system_group_args.add_argument('--post-system-stage-command',  metavar='', help='Commands to run after OS Packages are installed', action='append', default=[], dest='post-system-package-commands')

        spack_group_desc = 'The Spack stage of the Dockerfile provides Spack installations for the image.'
        spack_group_args = self.parser.add_argument_group('Spack Stage Arguments', spack_group_desc)
        spack_group_args.add_argument('-s', '--spack', help='Choose to install spack', default=True, dest='spack')
        spack_group_args.add_argument('-sv', '--spack-version', metavar='', help='The version of a Spack to install')
        spack_group_args.add_argument('-sc', '--spack-compiler', help='The Spack compiler that will be installed and will build Spack packages')
        spack_group_args.add_argument('-se', '--spack-env-file', metavar='', help='The path to a Spack env file')
        spack_group_args.add_argument('-p', '--spack-package', metavar='', help='The name of a Spack package to install', action='append', default=[], dest='spack-packages')
        spack_group_args.add_argument('--pre-spack-stage-command', metavar='', help='Commands to run before Spack is installed', action='append', default=[], dest='pre-spack-install-commands')
        spack_group_args.add_argument('--post-spack-install-command', metavar='', help='Commands to run after Spack is installed', action='append', default=[], dest='post-spack-install-commands')
        spack_group_args.add_argument('--post-spack-stage-command', metavar='', help='Commands to run after Spack Packages are installed', action='append', default=[], dest='post-spack-package-commands')

        return {'command': self, 'parser': self.parser}

    def check_arguments(self, arg_namespace):
        """Check if arguments provided in the command line are correct."""

        logger = Logger('core', '.logs.log', arg_namespace.verbose)

        # Print help if --help was provided
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
        """Run the command after checking the arguments"""

        self.check_arguments(arg_namespace)
        model = BuildModel(arg_namespace)
        model.build()
