import logging
from e4s_alc.controller.image.image import Image

logger = logging.getLogger('core')

class CentosImage(Image):
    def __init__(self, os_release):
        super().__init__(os_release)
        logger.info("Initializing CentosImage")
        self.pkg_manager_commands = None
        self.packages = [
            'curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim', 'environment-modules'
        ]
        self.update_cert_command = 'update-ca-trust'
        self.cert_location = '/etc/pki/ca-trust/source/anchors/'

    def get_version_commands(self, version):
        logger.debug("Getting version commands")
        commands = []

        if version == '8':
            swap_repo = 'swap centos-linux-repos centos-stream-repos'
            commands.extend([
                f'yum -y --disablerepo \'*\' --enablerepo=extras {swap_repo}',
                'yum -y distro-sync'
            ])

        return commands

    def get_pkg_manager_commands(self, added_packages):
        logger.debug("Getting pkg manager commands")
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

    def get_certificate_locations(self, certificates):
        logger.debug("Getting certificate locations")
        locations = []
        for cert in certificates:
            locations.append((cert, self.cert_location))
        return locations
