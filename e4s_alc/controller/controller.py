import logging
from e4s_alc.controller.image import SlesImage, CentosImage, UbuntuImage, RhelImage
from e4s_alc.controller.backend import DockerBackend, PodmanBackend, SingularityBackend

logger = logging.getLogger('core')

class Controller():
    def __init__(self, backend, base_image, repull=None):
        logger.info("Initializing Controller")
        self.backend = None
        # singularity-specific parameter
        self.repull = repull
        self.backend_str = backend
        if backend == 'podman':
            logger.debug("Setting backend to Podman")
            self.backend = PodmanBackend()
        if backend == 'docker':
            logger.debug("Setting backend to Docker")
            self.backend = DockerBackend()
        if backend == 'singularity':
            logger.debug("Setting backend to Singularity")
            self.backend = SingularityBackend()

        logger.debug(f"Getting OS from base image {base_image}")
        self.image = self.get_image_os(base_image)
        self.setup_script = '/etc/profile.d/setup-env.sh'

    def get_image_tag(self, base_image):
        logger.info("Getting tag from base image")
        image = None
        tag = None
        if ':' in base_image:
            image, tag = base_image.split(':')
        else:
            image, tag = base_image, 'latest'
        return image, tag

    def get_image_os(self, base_image):
        logger.info("Getting OS from base image")

        # Pull image
        image, tag = self.get_image_tag(base_image)
        logger.debug(f"Pulling base image {image}:{tag}")
        if self.backend_str == "singularity":
            self.backend.pull(image, tag, self.repull)
        else:
            self.backend.pull(image, tag)

        # Run the image with cat /etc/os-release
        os_release = self.backend.get_os_release(image, tag)
        os_id = os_release['ID']

        if os_id == 'sles':
            logger.debug("OS is SUSE Linux Enterprise Server")
            return SlesImage(os_release)

        if os_id == 'centos':
            logger.debug("OS is CentOS")
            return CentosImage(os_release)

        if os_id == 'ubuntu':
            logger.debug("OS is Ubuntu")
            return UbuntuImage(os_release)

        if os_id == 'rhel':
            logger.debug("OS is Red Hat Enterprise Linux")
            return RhelImage(os_release)

    def get_os_package_commands(self, os_packages):
        logger.info("Getting package manager commands for OS packages")
        return self.image.get_pkg_manager_commands(os_packages)

    def get_certificate_locations(self, certificates):
        logger.info("Getting certificate locations")
        return self.image.get_certificate_locations(certificates)

    def get_update_certificate_command(self):
        logger.info("Getting command to update certificates")
        return self.image.get_update_certificate_command()

    def get_env_setup_commands(self):        
        logger.info("Getting environment setup commands")
        commands = [
            f'echo "spack module tcl refresh -y" >> {self.setup_script}',
            f'echo ". /etc/profile.d/modules.sh" >> {self.setup_script}',
            f'echo ". /spack/share/spack/setup-env.sh" >> {self.setup_script}',
            f'echo "export MODULEPATH=\$(echo \$MODULEPATH | cut -d\':\' -f1)" >> {self.setup_script}'
        ]
        return commands

    def get_entrypoint_command(self):
        logger.info("Getting entrypoint command")
        commands = self.image.get_entrypoint_commands(self.setup_script)
        return '"' + '", "'.join(commands) + '"'

    def build(self):
        logger.info("Building Dockerfile with backend")
        self.backend.build()
