import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.create import CreateModel
from e4s_alc.cli.command import AbstractCommand
from e4s_alc import logger

LOGGER = logger.get_logger(__name__)

HELP_PAGE_FMT = "'%(command)s' page to be written."

class Create(AbstractCommand):
    def __init__(self, model):
        self.model = model()
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'Create a new image'

    def _construct_parser(self):
        usage = '%s create [options]' % self.command 
       
        self.parser.usage = usage

        yaml_or_package = self.parser.add_mutually_exclusive_group()
        yaml_or_package.add_argument('-p', '--package', nargs='+', metavar='\b', help='The name of a Spack package to install', default=[])
        yaml_or_package.add_argument('-y', '--yaml', metavar='\b', help='The yaml file used to specify spack packages to install')
        yaml_or_package.add_argument('-f', '--file', metavar='\b', help='The file used to create a new image')
        yaml_or_package.add_argument('-ns', '--no-spack', help='\b\b\b\bChoose to install spack', action='store_false', dest='spack')
        self.parser.add_argument('-i', '--image', metavar='\b', help='The image name and the tag <image:tag>')
        self.parser.add_argument('-n', '--name', metavar='\b', help='The name of the newly created image')
        self.parser.add_argument('-a', '--os-package', nargs='+', metavar='\b', help='The name of an OS Package to install', default=[])
        self.parser.add_argument('-c', '--copy', metavar='\b', help='Directory to copy into the image', action='append', default=[])
        self.parser.add_argument('-t', '--tarball', metavar='\b', help='Tarball to expand in the image', action='append', default=[])
        self.parser.add_argument('-P', '--parent', metavar='\b',help='Specific to singularity backend, choose which backend to use between Podman and Docker ["podman", "docker"] to prebuild the image', choices=['docker', 'podman'])
        self.parser.add_argument('-h', '--help', help='\b\b\b\b',action='store_true')

    def check_correct_args(self, args):
        if args.help:
            print()
            self.parser.print_help()
            print()
            exit(0)

        if not (args.image or args.name or args.file):
            LOGGER.error('Arguments \'-i/--image\' and \'-n/--name\' or \'-f/--file\' are required.')
            print()
            self.parser.print_help()
            print()
            exit(1)

        if (args.image or args.name) and args.file:
            LOGGER.error('Argument \'-f/--file\' cannot be used with argument \'-i/--image\' or \'-n/--name\'.')
            print()
            self.parser.print_help()
            print()
            exit(1)

        if (args.image or args.name) and not (args.image and args.name):
            print()
            LOGGER.error('Arguments \'-i/--image\' and \'-n/--name\' are both required.')
            self.parser.print_help()
            print()
            exit(1)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)

AbstractCommand.commands['create'] = Create(CreateModel)
