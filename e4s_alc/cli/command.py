from abc import ABCMeta, abstractmethod

class AbstractCommand(metaclass=ABCMeta):

    commands = {}

    def __init__(self, module_name, format_fields=None, summary_fmt=None, help_page_fmt=None, group=None):
        if not summary_fmt:
            summary_fmt = "No summary for '%(command)s'"
        if not help_page_fmt:
            help_page_fmt = "No help page for '%s(command)s'"
        self.module_name = module_name
        self.short_module_name = self.module_name.split('.')[-1]
        self.summary_fmt = summary_fmt
        self.help_page_fmt = help_page_fmt
        self.group = group
        self._parser = None


    def __str__(self):
        return self.command

    @property
    def summary(self):
        return self.summary_fmt % self.format_fields

    @property
    def help_page(self):
        return self.help_page_fmt % self.format_fields

    @property
    def parser(self):
        if self._parser is None:
            self._parser = self._construct_parser()
        return self._parser

    @property
    def usage(self):
        return self.parser.format_help()

    def add_subparser(self, subparsers):
        subparser_name = self.module_name.split('.')[-1]
        self._parser = subparsers.add_parser(subparser_name, help=self.parser_help)
        self._construct_parser()

    def _parse_args(self, argv):
        args = self.parser.parse_args(args=argv)
        return args

