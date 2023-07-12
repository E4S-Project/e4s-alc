import os
import subprocess
from e4s_alc.util import BackendFailedError
from e4s_alc.controller.backend import ContainerBackend
import logging

logger = logging.getLogger('core')

class DockerBackend(ContainerBackend):
    def __init__(self):
        logger.info("Initializing DockerBackend")
        super().__init__()
        self.program = 'docker'

    def pull(self, image, tag):
        logger.debug("Pulling Docker image")
        system_command = f'{self.program} pull {image}:{tag}'
        pull_success = not os.system(system_command)
        if not pull_success:
            logger.error("Failed to pull Docker image")
            raise BackendFailedError(self.program, system_command)

    def build(self):
        logger.debug("Building Docker image")
        build_command = f'{self.program} build .'
        build_success = not os.system(build_command)
        if not build_success:
            logger.error("Failed to build Docker image")
            raise BackendFailedError(self.program, build_command)

    def get_os_release(self, image, tag):
        logger.debug("Getting OS release of Docker image")
        container_command = 'cat /etc/os-release'
        system_command = f'{self.program} run {image}:{tag} {container_command}'
        system_command_output = subprocess.check_output(system_command, shell=True)
        if not system_command_output:
            logger.error("Failed to get OS release of Docker image")
            raise BackendFailedError(self.program, system_command)

        logger.debug('Stopping container')
        stop_container_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        stop_container_success = not os.system(stop_container_command)
        if not stop_container_success:
            logger.error("Failed to stop Docker container")
            raise BackendFailedError(self.program, stop_container_command)

        logger.debug('Removing container')
        remove_container_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        remove_container_success = not os.system(remove_container_command)
        if not remove_container_success:
            logger.error("Failed to remove Docker container")
            raise BackendFailedError(self.program, remove_container_command)

        logger.info("Parsing OS release information")
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')

        return os_release
