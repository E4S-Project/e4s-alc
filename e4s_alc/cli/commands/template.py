from e4s_alc.cli.commands.command import AbstractCommand

class TemplateCommand(AbstractCommand):
    """A class representing the Template Command, used to template a container by creating a Dockerfile."""

    def __init__(self):
        """Initialize the TemplateCommand class."""

        self.parser = None
        self.usage = 'e4s-alc template [options]'
        self.help = 'Create a template file for e4s-alc'

    def create_subparser(self, subparsers):
        """Create subparser and its attributes for this command."""

        self.parser = subparsers.add_parser('template',
                                            help=self.help,
                                            usage=self.usage,
                                            add_help=False,
                                            )
 
        self.parser.add_argument('-o', '--output', type=str, choices=['json', 'yaml'], help='Choose a format to output a message: json or yaml', default='yaml')
        self.parser.add_argument('-h', '--help', help='Display the help page', default=False, action='store_true', dest='help')
        return {'command': self, 'parser': self.parser}

    def check_arguments(self, arg_namespace):
        """Check if arguments provided in the command line are correct."""

        # Print help if --help was provided
        if arg_namespace.help:
            self.parser.print_help()
            exit(0)

    def run(self, arg_namespace):
        """Run the command after checking the arguments"""

        self.check_arguments(arg_namespace)
        print(self.create_yaml_template())

    def create_yaml_template(self):
        return """######## Base group ########
backend:
registry:
image:

initial-commands:
  - echo "Initial commands"

env-variables: 
  -

add-files: 
  -

post-base-stage-commands:
  - echo "Post base stage commands"

######## System group ########
pre-system-stage-commands: 
  - echo "Pre system stage commands"

certificates:
  -

os-packages: 
  -

post-system-stage-commands: 
  - echo "Command after installing system packages and before installing Spack"

####### Spack group #######
spack: True
spack-version:
spack-env-file: 
spack-packages: 
  -

pre-spack-stage-commands:
  - echo "Pre spack stage commands"

post-spack-install-commands: 
  - echo "Post spack install commands"

post-spack-stage-commands: 
  - echo "Post spack stage commands"
"""
