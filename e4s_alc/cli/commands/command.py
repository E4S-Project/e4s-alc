from abc import ABC, abstractmethod


class AbstractCommand(ABC):
    """
    AbstractCommand is an abstract base class that represents a general command structure.
    Concrete command classes should inherit from this class and provide implementations for
    all abstract methods.
    """

    @abstractmethod
    def create_subparser(self, subparsers):
        """Abstract method that all concrete command classes should implement.

        It is typically used to create a sub-parser specific to the command.

        Args:
            subparsers: Argument parser object to which sub-parser needs to be attached
        """
        
        pass

    @abstractmethod
    def check_arguments(self, arg_namespace):
        """Abstract method that all concrete command classes should implement.

        It is typically used to validate the command line arguments provided by the user.

        Args:
            arg_namespace: Parsed command line arguments
        """
        
        pass

    @abstractmethod
    def run(self, args):
        """Abstract method that all concrete command classes should implement.

        It is used to execute the actual logic of the command.

        Args:
            args: Parsed command line arguments
        """
        
        pass
