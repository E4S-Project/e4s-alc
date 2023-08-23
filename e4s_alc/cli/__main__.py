import argparse
from e4s_alc.cli.commands.create import CreateCommand
from e4s_alc.cli.commands.template import TemplateCommand
from e4s_alc.cli.cli_view import NoSubparsersMetavarFormatter

class MainCommand():
    """A class represents the main command of the CLI application."""
    
    def __init__(self):
        """Initialize the MainCommand class."""
        pass

    def main(self):
        """Create a command line parser and handle the provided command."""

        # Create a parser 
        parser = argparse.ArgumentParser(
            prog='e4s-alc',
            usage='%(prog)s [command] [options]',
            formatter_class=NoSubparsersMetavarFormatter
        )

        # Create subparsers
        subparsers = parser.add_subparsers(dest='command')

        # Initialize commands
        commands = [
            CreateCommand(),
            TemplateCommand()
        ]

        # Register each command's subparser and set the command as default for that subparser
        for command in commands:
            result_dict = command.create_subparser(subparsers)
            result_dict['parser'].set_defaults(command=result_dict['command'])

        # Parse arguments
        args = parser.parse_args()

        # If no command is specified, print help. Otherwise, run command.
        if args.command is None:
            parser.print_help()
        else:
            args.command.run(args)
        
# Instantiate the MainCommand class
COMMAND = MainCommand()
