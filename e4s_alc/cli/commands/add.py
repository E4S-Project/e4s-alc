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
        self.parser_help = 'Add help page'

    def _construct_parser(self):
        usage = '%s [arguments] <subcommand> [options]' % self.command 
        
        self.parser.add_argument('-n', '--name', metavar='\b', help='Image to name')
        self.parser.add_argument('-p', '--package', metavar='\b', help='Package name', action='append', default=[])
        self.parser.add_argument('-a', '--os-package', metavar='\b', help='OS Package name', action='append', default=[])
        self.parser.add_argument('-c', '--copy', metavar='\b', help='File/directory to copy into the Image', action='append', default=[])

    def check_correct_args(self, args):
        if not args.name:
            print('Error: Argument \'-n/--name\' is required.')
            exit(1)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)

AbstractCommand.commands['add'] = Add(AddModel)
