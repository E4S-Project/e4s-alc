from e4s_alc.util import log_function_call
from e4s_alc.controller.image.image import Image

class RockyImage(Image):
    """
    A class representing a Rocky Image.
    """

    @log_function_call
    def __init__(self, os_release):
        """
        Initializes a RockyImage object.

        Args:
            os_release (str): The OS version for the image.
        """
        super().__init__(os_release)
        self.pkg_manager_commands = None
        self.packages = [
            'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
            'gnupg2', 'hostname', 'iproute', 'make', 'patch', 'bzip2',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'
        ]
        self.update_cert_command = 'update-ca-trust'
        self.cert_location = '/etc/pki/ca-trust/source/anchors/'

    @log_function_call
    def get_version_commands(self, version):
        """
        Returns an empty command list for given version. To be implemented in subclasses.

        Args:
            version (str): The OS version.

        Returns:
            list: An empty list of commands. 
        """
        commands = []
        return commands

    @log_function_call
    def get_package_manager_commands(self, added_packages):
        """
        Returns the package manager commands for given additional packages.

        Args:
            added_packages (list): Additional packages to be added. 

        Returns:
            list: A list of package manager commands. 
        """
        self.packages.extend(added_packages)
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        self.pkg_manager_commands = self.get_version_commands(self.version)
        self.pkg_manager_commands.extend([
            'yum update -y',
            f'yum install -y {self.packages}',
        ])
        return self.pkg_manager_commands

    @log_function_call
    def get_certificate_locations(self, certificates):
        """
        Returns a list of tuples containing certificate and location.

        Args:
            certificates (list): List of certificate file names.

        Returns:
            list: A list of tuples, each containing a certificate file name and its location.
        """
        locations = []
        for cert in certificates:
            locations.append((cert, self.cert_location))
        return locations

    @log_function_call
    def get_entrypoint_commands(self, setup_script):
        """
        Returns the entrypoint command list for given setup script.

        Args:
            setup_script (str): The setup script. 

        Returns:
            list: A list of entrypont commands. 
        """
        commands = ['/bin/bash']
        return commands
