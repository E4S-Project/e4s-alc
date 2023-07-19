import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.init import InitModel
from e4s_alc.cli.command import AbstractCommand

HELP_PAGE_FMT = "'%(command)s' page to be written."

from e4s_alc.model.container import SUPPORTED_BACKENDS

class Init(AbstractCommand):
    def __init__(self, model):
        self.model = model()
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'Initialize e4s-alc backend'
    
    def _construct_parser(self):
        usage = '%s init [options]' % self.command 
        
        self.parser.usage = usage
        self.parser.add_argument('-b', '--backend', metavar='\b', help='Backend for containers, currently supported options: {}'.format(list(SUPPORTED_BACKENDS.keys())), choices=['docker', 'podman', 'singularity'])
        self.parser.add_argument('-P', '--parent', metavar='\b',help='Specific to singularity backend, choose which backend to use between Podman and Docker ["podman", "docker"] to only try initialising the backend with', choices=['docker', 'podman'], default=None)
        self.parser.add_argument('-h', '--help', action='store_true')

    def check_correct_args(self, args):
        if args.help:
            self.parser.print_help()
            print()
            exit(0)

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)


AbstractCommand.commands['init'] = Init(InitModel)
