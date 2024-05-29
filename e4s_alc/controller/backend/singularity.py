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

    def pull(self, image, tag, repull=None):

        def execute_pull():
            system_command = f'{self.program} pull --disable-cache --dir {self.image_dir} {image}:{tag}'
            pull_success = not os.system(system_command)
            if not pull_success:
                logger.error("Failed to pull Singularity image, trying with docker registry:")
                system_command_docker_reg = f'{self.program} pull --disable-cache --dir {self.image_dir} docker://{image}:{tag}'
                pull_success = not os.system(system_command_docker_reg)
                if not pull_success:
                    logger.error("Failed to pull Singularity image")
                    raise BackendFailedError(self.program, system_command)

        logger.debug("Pulling image")
        image_name = f'{image.split("/")[-1]}_{tag}.sif'
        image_path = f'{SINGULARITY_IMAGES}{image_name}'
        if os.path.exists(image_path):
            if repull is not None:
                if repull:
                    os.remove(image_path)
                    execute_pull()
            else:
                delete_image = input(f"WARNING: An image named {image_name} has been found. Should that image be used? If not, it will be removed. [Y/n]\n")
                if delete_image in ['n', 'N', 'no']:
                    print(f"Removed {image_path} and pulling a new one.")
                    os.remove(image_path)
                    execute_pull()
                else:
                    print(f"Using {image_path} instead of pulling new one.")
        else:
            execute_pull()

    def get_os_release(self, image, tag):
        logger.debug("Getting OS release of the image")
        container_command = 'cat /etc/os-release'
        system_command = f'{self.program} exec {self.image_dir}/{image}_{tag}.sif {container_command}'
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
