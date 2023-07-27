import os
import subprocess
from e4s_alc.util import BackendFailedError
from e4s_alc.controller.backend import ContainerBackend
import logging

logger = logging.getLogger('core')

SINGULARITY_IMAGES = os.path.expanduser("~") + "/.e4s-alc/singularity_images/"

class SingularityBackend(ContainerBackend):
    def __init__(self):
        logger.info("Initializing SingularityBackend")
        super().__init__()
        self.program = 'singularity'
        self.image_dir = SINGULARITY_IMAGES
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)

    def pull(self, image, tag):
        logger.debug("Pulling image")
        system_command = f'{self.program} pull --dir {self.image_dir} {image}:{tag}'
        pull_success = not os.system(system_command)
        if not pull_success:
            logger.error("Failed to pull Singularity image")
            raise BackendFailedError(self.program, system_command)

#    def build(self):
#        logger.debug("Building Singularity image")
#        build_command = f'{self.program} build --fakeroot '
#        build_success = not os.system(build_command)
#        if not build_success:
#            logger.error("Failed to build Singularity image")
#            raise BackendFailedError(self.program, build_command)

    def get_os_release(self, image, tag):
        logger.debug("Getting OS release of the image")
        container_command = 'cat /etc/os-release'
        system_command = f'{self.program} exec {self.image_dir}/{image} {container_command}'
        system_command_output = subprocess.check_output(system_command, shell=True)
        if not system_command_output:
            logger.error("Failed to get OS release of the image")
            raise BackendFailedError(self.program, system_command)

        logger.info("Parsing OS release information")
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')

        return os_release
