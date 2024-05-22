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
        self.parser.add_argument('-n', '--name', help='Name of the output file')
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
        if arg_namespace.output == "yaml":
            print(self.create_yaml_template())
        else:
            print(self.create_json_template())

    def create_yaml_template(self):
        return """######## Base group ########
backend:
registry:
image:

initial-commands:
  -

env-variables: 
  -

add-files: 
  -

post-base-stage-commands:
  -

######## System group ########
pre-system-stage-commands: 
  -

certificates:
  -

os-packages: 
  -

add-remote-files:
  -

add-repos:
  -

post-system-stage-commands: 
  -

####### Spack group #######
spack: True
pre-spack-stage-commands:
  -

spack-version:
spack-mirrors:
  -

spack-check-signature: True
modules-yaml-file: 
post-spack-install-commands: 
  -

spack-yaml-file: 
spack-compiler:
spack-packages: 
  -

post-spack-stage-commands: 
  -
  
####### Matrix group #######
registry-image-matrix:
  -

spack-version-matrix:
  - 

spack-compiler-matrix:
  -"""

    def create_json_template(self):
       return """ {
    "backend": null,
    "registry": null,
    "image": null,
    "initial-commands": [null],
    "env-variables": [null],
    "add-files": [null],
    "post-base-stage-commands": [null],
    "pre-system-stage-commands": [null],
    "certificates": [null],
    "os-packages": [null],
    "add-remote-files": [null],
    "add-repos": [null],
    "post-system-stage-commands": [null],
    "spack": true,
    "pre-spack-stage-commands": [null],
    "spack-version": null,
    "spack-mirrors": [null],
    "spack-check-signature": true,
    "modules-yaml-file": null,
    "post-spack-install-commands": [null],
    "spack-yaml-file": null,
    "spack-compiler": null,
    "spack-packages": [null],
    "post-spack-stage-commands": [null],
    "registry-image-matrix": [null],
    "spack-version-matrix": [null],
    "spack-compiler-matrix": [null]
}"""
