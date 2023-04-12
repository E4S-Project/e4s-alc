import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.list import ListModel
from e4s_alc.cli.command import AbstractCommand

HELP_PAGE_FMT = "'%(command)s' page to be written."

class List(AbstractCommand):
    def __init__(self, model):
        self.model = model()
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'List images'

    def _construct_parser(self):
        usage = '%s add [options]' % self.command 
        
        self.parser.usage = usage
        self.parser.add_argument('-n', '--name', metavar='', help='The name of a specific image to show')
        self.parser.add_argument('-a', '--all', dest="inter", help='Includes intermediate images', action='store_true')
        self.parser.add_argument('-h', '--help', action='store_true')

    def check_correct_args(self, args):
        if args.help:
            print()
            self.parser.print_help()
            print()
            exit(0)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)

AbstractCommand.commands['list'] = List(ListModel)
