import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.create import CreateModel
from e4s_alc.cli.command import AbstractCommand

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
        self.parser.add_argument('-i', '--image', metavar='\b', help='The image name and the tag <image:tag>')
        self.parser.add_argument('-n', '--name', metavar='\b', help='The name of the newly created image')
        self.parser.add_argument('-p', '--package', metavar='\b', help='The name of a Spack package to install', action='append', default=[])
        self.parser.add_argument('-a', '--os-package', metavar='\b', help='The name of an OS Package to install', action='append', default=[])
        self.parser.add_argument('-c', '--copy', metavar='\b', help='Directory to copy into the image', action='append', default=[])
        self.parser.add_argument('-t', '--tarball', metavar='\b', help='Tarball to expand in the image', action='append', default=[])
        self.parser.add_argument('-f', '--file', metavar='\b', help='The file used to create a new image')
        self.parser.add_argument('-h', '--help', action='store_true')

    def check_correct_args(self, args):
        if args.help:
            print()
            self.parser.print_help()
            print()
            exit(0)

        if not (args.image or args.name or args.file):
            print('Error: Arguments \'-i/--image\' and \'-n/--name\' or \'-f/--file\' are required.')
            print()
            self.parser.print_help()
            print()
            exit(1)

        if (args.image or args.name) and args.file:
            print('Error: Argument \'-f/--file\' cannot be used with argument \'-i/--image\' or \'-n/--name\'.')
            print()
            self.parser.print_help()
            print()
            exit(1)

        if (args.image or args.name) and not (args.image and args.name):
            print()
            print('Error: Arguments \'-i/--image\' and \'-n/--name\' are both required.')
            self.parser.print_help()
            print()
            exit(1)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)

AbstractCommand.commands['create'] = Create(CreateModel)
