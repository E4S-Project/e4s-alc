from e4s_alc.util import log_function_call
from e4s_alc.controller.image.image import Image

class UbuntuImage(Image):
    """
    Class to represent an Ubuntu Image with its essential and additional packages, 
    certificate locations and other properties. Inherits from the Image class.
    """

    @log_function_call
    def __init__(self, os_release):
        """
        Initializes the UbuntuImage instance with essential packages and certificate locations.

        Args:
            os_release (str): OS release version.
        """
        super().__init__(os_release)
        #Essential packages for Ubuntu Image.
        self.packages = [
            'build-essential', 'ca-certificates', 'coreutils', 'curl', 'file',
            'environment-modules', 'gfortran', 'git', 'gpg', 'lsb-release', 'vim',
            'python3', 'python3-distutils', 'python3-venv', 'unzip', 'zip', 'cmake'
        ]
        self.update_cert_command = 'update-ca-certificates'
        self.cert_location = '/usr/local/share/ca-certificates/'

    @log_function_call
    def get_version_commands(self, version):
        """
        Method to get version commands. Intended to be implemented in derived classes.

        Args:
            version (str): Version string.

        Returns:
            list: Empty list as the base implementation.
        """
        commands = []
        return commands

    @log_function_call
    def get_package_manager_commands(self, added_packages):
        """
        Method to get package manager commands after adding new packages.

        Args:
            added_packages (list): list of new packages to be added.

        Returns:
            list: List of package manager commands.
        """
        self.packages.extend(added_packages)
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        self.pkg_manager_commands = self.get_version_commands(self.version)
        self.pkg_manager_commands.extend([
            'apt-get update',
            f'apt-get install -y {self.packages}'
        ])
        return self.pkg_manager_commands

    @log_function_call
    def get_certificate_locations(self, certificates):
        """
        Method to get certificate locations.

        Args:
            certificates (list): List of certificates.

        Returns:
            list: List of tuples containing certificate and its converted path.
        """
        locations = []
        for cert in certificates:
            locations.append((cert, self.convert_cert_path(cert)))
        return locations

    @log_function_call
    def get_entrypoint_commands(self, setup_script):
        """
        Method to get entry point commands.

        Args:
            setup_script (str): path to the setup script.

        Returns:
            list: List of entry point commands.
        """
        commands = ['/bin/bash', '-c', f'. {setup_script} && exec /bin/bash']
        return commands
