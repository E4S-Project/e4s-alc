import os
import logging
import subprocess
from e4s_alc.util import BackendFailedError
from e4s_alc.controller.backend import ContainerBackend

logger = logging.getLogger('core')

class PodmanBackend(ContainerBackend):
    def __init__(self):
        super().__init__()
        logger.info("Initializing PodmanBackend")
        self.program = 'podman'

    def pull(self, image, tag):
        logger.debug("Pulling image")
        pull_command = f'{self.program} pull {image}:{tag}'
        pull_success = not os.system(pull_command)
        if not pull_success:
            logger.error("Failed to pull image")
            raise BackendFailedError(self.program, pull_command)

    def build(self):
        logger.debug("Building image")
        build_command = f'{self.program} build .'
        build_success = not os.system(build_command)
        if not build_success:
            logger.error("Failed to build image")
            raise BackendFailedError(self.program, build_command)

    def get_os_release(self, image, tag):
        logger.debug("Getting OS release of Podman image")
        container_command = 'cat /etc/os-release'
        system_command = f'{self.program} run {image}:{tag} {container_command}'
        try:
            system_command_output = subprocess.check_output(system_command, shell=True)
        except subprocess.CalledProcessError as e:
            logger.error("Failed to get os release")
            raise BackendFailedError(self.program, system_command) from e

        logger.debug("Stopping container")
        stop_container_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        stop_container_success = not os.system(stop_container_command)
        if not stop_container_success:
            logger.error("Failed to stop container")
            raise BackendFailedError(self.program, stop_container_command)

        logger.debug("Removing container")
        remove_container_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        remove_container_success = not os.system(remove_container_command)
        if not remove_container_success:
            logger.error("Failed to remove container")
            raise BackendFailedError(self.program, remove_container_command)

        logger.info('Parsing OS release information')
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')

        return os_release
