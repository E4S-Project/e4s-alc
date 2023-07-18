import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.add import AddModel
from e4s_alc.cli.command import AbstractCommand
from e4s_alc import logger

LOGGER = logger.get_logger(__name__)

HELP_PAGE_FMT = "'%(command)s' page to be written."

class Add(AbstractCommand):
    def __init__(self, model):
        self.model = model()
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'Add to an existing image'

    def _construct_parser(self):
        usage = '%s add [options]' % self.command

        self.parser.usage = usage

        yaml_or_package = self.parser.add_mutually_exclusive_group()
        yaml_or_package.add_argument('-p', '--package', nargs='+', metavar='\b', help='The name of a Spack package to install', default=[])
        yaml_or_package.add_argument('-y', '--yaml', metavar='\b', help='The yaml file used to specify a spack environment to install')
        yaml_or_package.add_argument('-f', '--file', metavar='\b', help='The file used to create a new image')

        self.parser.add_argument('-n', '--name', metavar='\b', help='The name of the image to add to')
        self.parser.add_argument('-a', '--os-package', nargs='+', metavar='\b', help='The name of an OS Package to install', default=[])
        self.parser.add_argument('-c', '--copy', metavar='\b', help='Directory to copy into the image', action='append', default=[])
        self.parser.add_argument('-t', '--tarball', metavar='\b', help='Tarball to expand in the image', action='append', default=[])
        self.parser.add_argument('-P', '--parent', metavar='\b', help='Specific to singularity backend, choose which backend to use between Podman and Docker ["podman", "docker"] to add to the image', choices=['docker', 'podman'])
        self.parser.add_argument('-h', '--help', action='store_true')

    def check_correct_args(self, args):
        if args.help:
            print()
            self.parser.print_help()
            print()
            exit(0)

        if not (args.name or args.file):
            LOGGER.error('Argument \'-n/--name\' is required.')
            print()
            self.parser.print_help()
            print()
            exit(1)

    def check_modifies(self, args):
        if not (args.package or args.os_package or args.copy or args.tarball or args.file or args.yaml):
            LOGGER.error("This command doesn't apply any modifications the image.")
            print()
            self.parser.print_help()
            print()
            exit(1)


    def main(self, args):
        self.check_correct_args(args)
        self.check_modifies(args)
        self.model.main(args)

AbstractCommand.commands['add'] = Add(AddModel)
