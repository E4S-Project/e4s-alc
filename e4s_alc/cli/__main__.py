import os
import sys
import e4s_alc
import argparse
from e4s_alc import E4S_ALC_VERSION, E4S_ALC_URL, E4S_ALC_SCRIPT
from e4s_alc.cli.cli_view import NoSubparsersMetavarFormatter
from e4s_alc.cli.command import AbstractCommand
import e4s_alc.cli.commands

try:
    from e4s_alc.version import __version__
except ModuleNotFoundError:
    # the version.py file is created dynamically at install.
    # This should only fail when the code is run in an unsupported manner
    __version__ = 'DEV0.0'

HELP_PAGE_FMT = "'%(command)s' page to be written."

class MainCommand(AbstractCommand):
    """Main entry point to the command line interface."""

    def __init__(self):
        summary_parts = ["E4S-ALC %s " % E4S_ALC_VERSION, E4S_ALC_URL]
        super().__init__(__name__, summary_fmt=''.join(summary_parts), help_page_fmt=HELP_PAGE_FMT)
        self.command = os.path.basename(E4S_ALC_SCRIPT)

    def _construct_parser(self):
        usage = '%s [arguments] [options]' % self.command 
        description = 'E4S à la carte is a tool that allows a user to customize a container image by adding packages to it. These can be system packages and Spack packages.'

        parser = argparse.ArgumentParser(
                    prog = 'e4s-alc',
                    usage = usage,
                    description = description,
                    formatter_class = NoSubparsersMetavarFormatter)

        subparsers = parser.add_subparsers(dest='command')
        for command in AbstractCommand.commands.values():
            command.add_subparser(subparsers)

        parser.add_argument('-V', '--version', help='Show programs version number and exit.', action='store_true')
        parser.add_argument('-q', '--quiet', help='Suppress all output except error messages.', action='store_true')
        parser.add_argument('-v', '--verbose', help='Show debugging messages.', action='store_true')

        return parser 

    def main(self, argv):
        if not len(sys.argv) > 1:
            self.parser.print_help()
            print()
            exit(1)

        args = self._parse_args(argv)

        if args.version:
            print(__version__)
            return 0

        command = args.command
        AbstractCommand.commands[command].main(args)


COMMAND = MainCommand()

if __name__ == '__main__':
    sys.exit(COMMAND.main(sys.argv[1:]))
