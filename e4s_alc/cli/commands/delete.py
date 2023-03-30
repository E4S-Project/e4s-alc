import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.delete import DeleteModel
from e4s_alc.cli.command import AbstractCommand

HELP_PAGE_FMT = "'%(command)s' page to be written."

class Delete(AbstractCommand):
    def __init__(self, model):
        self.model = model()
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'Delete the specified image'

    def _construct_parser(self):
        usage = '%s delete [options]' % self.command      
        self.parser.usage = usage
        self.parser.add_argument('-n', '--name', metavar='', help='The name of the image to delete')
        self.parser.add_argument('-f', '--force', help='Attempt to force the deletion', action='store_true')
        self.parser.add_argument('-p', '--prune', help='Delete unused images', action='store_true')
        self.parser.add_argument('-c', '--prune-containers', help='Delete stopped containers', action='store_true')
        self.parser.add_argument('-h', '--help', help='\b\b\b\b',action='store_true')

    def check_correct_args(self, args):
        if args.help:
            print()
            self.parser.print_help()
            print()
            exit(0)

        if not (args.name or args.prune or args.prune_containers):
            print('Error: Arguments \'-n/--name\' or \'-p/--prune\' or \'-c/--prune-containers\' is required.')
            print()
            self.parser.print_help()
            print()
            exit(1)

        if args.name and args.prune:
            print('Error: Arguments \'-n/--name\' and \'-p/--prune\' and \'-c/--prune-containers\' can\'t be used together.')
            print()
            self.parser.print_help()
            print()
            exit(1)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)

AbstractCommand.commands['delete'] = Delete(DeleteModel)