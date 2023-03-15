import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.add import AddModel
from e4s_alc.cli.command import AbstractCommand

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
        self.parser.add_argument('-n', '--name', metavar='\b', help='The name of the image to add to')
        self.parser.add_argument('-p', '--package', metavar='\b', help='The name of a Spack package to install', action='append', default=[])
        self.parser.add_argument('-a', '--os-package', metavar='\b', help='The name of an OS Package to install', action='append', default=[])
        self.parser.add_argument('-c', '--copy', metavar='\b', help='Directory to copy into the image', action='append', default=[])
        self.parser.add_argument('-t', '--tarball', metavar='\b', help='Tarball to expand in the image', action='append', default=[])
        self.parser.add_argument('-f', '--file', metavar='\b', help='The file used to add to a image')
        self.parser.add_argument('-h', '--help', action='store_true')

    def check_correct_args(self, args):
        if args.help:
            print()
            self.parser.print_help()
            print()
            exit(0)

        if not (args.name or args.file):
            print('Error: Argument \'-n/--name\' is required.')
            print()
            self.parser.print_help()
            print()
            exit(1)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)

AbstractCommand.commands['add'] = Add(AddModel)
