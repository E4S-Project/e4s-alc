import logging
from e4s_alc.controller.image.image import Image

logger = logging.getLogger('core')

class SlesImage(Image):
    def __init__(self, os_release):
        super().__init__(os_release)
        logger.info("Initializing SlesImage")
        self.packages = [
            'curl', 'gzip', 'tar', 'python3', 'python3-pip', 'gcc',
            'gcc-c++', 'gcc-fortran', 'patch', 'make', 'gawk', 'xz',
            'cmake', 'bzip2', 'vim', 'environment-modules'
        ]
        self.update_cert_command = 'update-ca-trust'

    def get_version_commands(self, version):
        logger.debug(f"Getting version commands")
        commands = []
        return commands

    def get_pkg_manager_commands(self, added_packages):
        logger.debug(f"Getting package manager commands")
        self.packages.extend(added_packages)
        self.packages = ' '.join(self.packages)
        self.packages = self.wrap_packages(self.packages)

        self.pkg_manager_commands = self.get_version_commands(self.version)
        self.pkg_manager_commands.extend([
            'zypper update',
            f'zypper install -y {self.packages}'
        ])
        return self.pkg_manager_commands

    def get_certificate_locations(self, certificates):
        logger.debug("Getting certificate locations")
        locations = []
        for cert in certificates:
            locations.append((cert, self.cert_location))
        return locations
