from e4s_alc.util import log_function_call, log_info
from e4s_alc.controller.image.image import Image

version_packages = {
        'default': ['curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch', 'bzip2',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
        '8.10': ['curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch', 'bzip2',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
        '9.4': ['findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  'xz',
            'gnupg2', 'hostname', 'iproute', 'make', 'patch', 'bzip2',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'],
    }

class RhelImage(Image):
    """
    This class represents an object of Red Hat Enterprise Linux Image.
    Inherits from the Image base class.
    """

    @log_function_call
    def __init__(self, os_release):
        """
        Initialises the RhelImage with given OS release and
        sets the package manager commands, required packages and certificate details.

        Args:
            os_release (str): Release version of the operating system.
        """
        super().__init__(os_release)
        self.pkg_manager_commands = None
        os_version = os_release["VERSION_ID"]
        if os_version in version_packages.keys():
            self.packages = version_packages[os_version]
        else:
            self.packages = version_packages["default"]
        self.update_cert_command = 'update-ca-trust'
        self.cert_location = '/etc/pki/ca-trust/source/anchors/'

    @log_function_call
    def get_version_commands(self, version):
        """
        Returns the list of commands based on version.

        Args:
            version (str): Version string.

        Returns:
            commands (list): List of commands.
        """
        commands = []
        return commands

    @log_function_call
    def get_package_manager_commands(self, added_packages):
        """
        Extends the package list, wraps the packages and gives list of package manager commands.

        Args:
            added_packages (list) : List of additional packages to be installed.

        Returns:
            pkg_manager_commands (list) : List of package manager commands required.
        """
        log_info(f"Adding packages: {added_packages}")
        self.packages.extend(added_packages)

        log_info("Joining the packages into a single string.")
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        log_info("Getting package manager commands based on the version.")
        self.pkg_manager_commands = self.get_version_commands(self.version)

        log_info("Adding update and installation commands for the packages.")
        self.pkg_manager_commands.extend([
            'yum update -y',
            f'yum install -y {self.packages}',
        ])
        return self.pkg_manager_commands

    @log_function_call
    def get_certificate_locations(self, certificates):
        """
        Appends the path of the certificate files to the list of locations.

        Args:
            certificates (list) : List of certificates.

        Returns:
            locations (list) : List of tuples containing certificate and its path.
        """
        locations = []

        log_info(f"Looping over certificates: {certificates}.")
        for cert in certificates:
            log_info(f"Appending certificate: {cert} with location: {self.cert_location}.")
            locations.append((cert, self.cert_location))

        return locations

    @log_function_call
    def get_entrypoint_commands(self, setup_script):
        """
        Returns the list of entrypoint commands.

        Args:
            setup_script (str) : Script to setup entrypoints.

        Returns:
            commands (list) : List of commands.
        """
        commands = ['/bin/bash' , '-c', f'. {setup_script} && exec /bin/bash']
        return commands
