from e4s_alc.util import log_function_call
from e4s_alc.controller.image.image import Image

class CentosImage(Image):
    """
    A class that defines a CentosImage extending the Image class.
    """

    @log_function_call
    def __init__(self, os_release):
        """
        Initializes the CentosImage and sets the basic packages and certificate locations.

        Args:
            os_release (str): The OS release version.

        """
        super().__init__(os_release)
        self.pkg_manager_commands = None
        self.packages = [
            'curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'
        ]
        self.update_cert_command = 'update-ca-trust'
        self.cert_location = '/etc/pki/ca-trust/source/anchors/'

    @log_function_call
    def get_version_commands(self, version):
        """
        Returns the commands required for specific CentOS version.

        Args:
            version (str): CentOS version.

        Returns:
            list: List of commands required for the specific CentOS version.
        """
        commands = []

        if version == '8':
            swap_repo = 'swap centos-linux-repos centos-stream-repos'
            commands.extend([
                f'yum -y --disablerepo \'*\' --enablerepo=extras {swap_repo}',
                'yum -y distro-sync'
            ])

        return commands

    @log_function_call
    def get_package_manager_commands(self, added_packages):
        """
        Returns the commands required to install packages.

        Args:
            added_packages (list): List of additional packages to be installed.

        Returns:
            list: List of commands required to install packages.
        """
        self.packages.extend(added_packages)
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        self.pkg_manager_commands = self.get_version_commands(self.version)
        self.pkg_manager_commands.extend([
            'yum update -y',
            'yum install epel-release -y',
            'yum --enablerepo epel groupinstall -y "Development Tools"',
            f'yum --enablerepo epel install -y {self.packages}',
        ])
        return self.pkg_manager_commands

    @log_function_call
    def get_certificate_locations(self, certificates):
        """
        Returns the list of locations for the given certificates.

        Args:
            certificates (str): Certificates.

        Returns:
            list: List of tuples where each tuple contains a certificate and its location.
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
