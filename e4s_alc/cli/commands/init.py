import os
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.model.init import InitModel
from e4s_alc.cli.command import AbstractCommand

HELP_PAGE_FMT = "'%(command)s' page to be written."

class Init(AbstractCommand):
    def __init__(self, model):
        self.model = model()
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)
        self.parser_help = 'Init help page'
    
    def _construct_parser(self):
        usage = '%s [arguments] <subcommand> [options]' % self.command 
        
        self.parser.add_argument('-b', '--backend', metavar='\b', help='Backend for containers')

    def check_correct_args(self, args):
        pass

    def main(self, args):
        self.check_correct_args(args)
        self.model.main(args)


AbstractCommand.commands['init'] = Init(InitModel)
