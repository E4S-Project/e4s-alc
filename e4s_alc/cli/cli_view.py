from argparse import ArgumentParser, HelpFormatter, _SubParsersAction, HelpFormatter

class HelpDescriptionFormatter(HelpFormatter):
    def __init__(self, prog):
        super().__init__(prog, max_help_position=52)

    def _format_action_invocation(self, action):
        if not action.option_strings:
            part = super()._format_action_invocation(action)
        else:
            part = ', '.join(action.option_strings)
        return part

class NoSubparsersMetavarFormatter(HelpFormatter):
    """
    This class provides custom formatting for the help text display.
    It inherits from the HelpFormatter class provided by argparse.
    This formatter removes the metavar and indentation from subparsers.
    """

    def _format_action(self, action):
        """Formats the help text for a specific action."""
        
        result = super()._format_action(action)
        if isinstance(action, _SubParsersAction):
            # Correct the indentation on the first line
            return "%*s%s" % (self._current_indent, "", result.lstrip())
        return result

    def _format_action_invocation(self, action):
        """Formats the display of the action invocation syntax."""
        
        if isinstance(action, _SubParsersAction):
            # Remove metavar and help lines for subparsers
            return ""
        return super()._format_action_invocation(action)

    def _iter_indented_subactions(self, action):
        """Provides an iterator over subactions with adjusted indentation."""
        
        if isinstance(action, _SubParsersAction):
            try:
                get_subactions = action._get_subactions
            except AttributeError:
                # If 'action' does not have attribute '_get_subactions', pass
                pass
            else:
                # Remove indentation for subparsers
                yield from get_subactions()
        else:
            yield from super()._iter_indented_subactions(action)
