import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.cli.command import AbstractCommand

HELP_PAGE_FMT = "'%(command)s' page to be written."

class Create(AbstractCommand):
    def __init__(self):
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'Create help page'

    def _construct_parser(self):
        usage = '%s [arguments] <subcommand> [options]' % self.command 
        
        self.parser.add_argument('-i', '--image', metavar='\b', help='Image name')
        self.parser.add_argument('-n', '--name', metavar='\b', help='Image to name')
        self.parser.add_argument('-p', '--package', metavar='\b', help='Package name', action='append')
        self.parser.add_argument('-a', '--os-package', metavar='\b', help='OS Package name', action='append')
        self.parser.add_argument('-f', '--file', metavar='\b', help='File to create Image')

    def check_correct_args(self, args):
        if not (args.image or args.name or args.file):
            print('Error: Arguments \'-i/--image\' and \'-n/--name\' or \'-f/--file\' are required.')
            exit(1)

        if (args.image or args.name) and args.file:
            print('Error: Argument \'-f/--file\' cannot be used with argument \'-i/--image\' or \'-n/--name\'.')
            exit(1)

        if (args.image or args.name) and not (args.image and args.name):
            print('Error: Arguments \'-i/--image\' and \'-n/--name\' are both required.')
            exit(1)

    def main(self, args):
        print('CREATE', args)
        self.check_correct_args(args)

AbstractCommand.commands['create'] = Create()
