import logging
from e4s_alc.controller.image.image import Image

logger = logging.getLogger('core')

class UbuntuImage(Image):
    def __init__(self, os_release):
        super().__init__(os_release)
        logger.info(" Initializing UbuntuImage")
        self.packages = [
            'build-essential', 'ca-certificates', 'coreutils', 'curl',
            'environment-modules', 'gfortran', 'git', 'gpg', 'lsb-release', 'vim',
            'python3', 'python3-distutils', 'python3-venv', 'unzip', 'zip', 'cmake'
        ]
        self.update_cert_command = 'update-ca-certificates'
        self.cert_location = '/usr/local/share/ca-certificates/'

    def get_version_commands(self, version):
        logger.debug("Getting version commands")
        commands = []
        return commands

    def get_pkg_manager_commands(self, added_packages):
        logger.debug("Getting pkg manager commands")
        self.packages.extend(added_packages)
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        self.pkg_manager_commands = self.get_version_commands(self.version)
        self.pkg_manager_commands.extend([
            'apt-get update',
            f'apt-get install -y {self.packages}'
        ])
        return self.pkg_manager_commands

    def get_certificate_locations(self, certificates):
        logger.debug("Getting certificate locations")
        locations = []
        for cert in certificates:
            locations.append((cert, self.convert_cert_path(cert)))
        return locations
