from e4s_alc.util import log_function_call
from e4s_alc.controller.image.image import Image

class SlesImage(Image):
    """
    Derived class from Image specifically for Suse Linux Enterprise Server.
    """
    @log_function_call
    def __init__(self, os_release):
        """
        Create a new SLES image. Initializes the base attributes and provides an initial set of packages.

        Args:
            os_release (str): operating system release version.
        """
        super().__init__(os_release)
        self.packages = [
            'curl', 'gzip', 'tar', 'python3', 'python3-pip', 'gcc',
            'gcc-c++', 'gcc-fortran', 'patch', 'make', 'gawk', 'xz',
            'cmake', 'bzip2', 'vim', 'environment-modules'
        ]
        self.update_cert_command = 'update-ca-trust'

    @log_function_call
    def get_version_commands(self, version):
        """
        Get the version-specific commands for SLES.

        Args:
            version (str): Version string.

        Returns:
            List: A list of commands. Currently, it returns an empty list.
        """
        commands = []
        return commands

    @log_function_call
    def get_package_manager_commands(self, added_packages):
        """
        Returns the commands for the package manager to install additional packages.

        Args:
            added_packages (list): A list of additional packages to be installed.

        Returns:
            List: A list of commands to be executed by the package manager.
        """
        self.packages.extend(added_packages)
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        self.pkg_manager_commands = self.get_version_commands(self.version)
        self.pkg_manager_commands.extend([
            'zypper update',
            f'zypper install -y {self.packages}'
        ])
        return self.pkg_manager_commands

    @log_function_call
    def get_certificate_locations(self, certificates):
        """
        Get the locations of the specified certificates.

        Args:
            certificates (list): A list of certificate paths.

        Returns:
            List: A list of tuples, each one containing a certificate and its location.
        """
        locations = []
        for cert in certificates:
            locations.append((cert, self.cert_location))
        return locations
