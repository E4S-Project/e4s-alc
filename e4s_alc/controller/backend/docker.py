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

    def system_call(self, command):
        call_success = not os.system(command)
        if not call_success:
            logger.error("System command failed")
            raise BackendFailedError(self.program, command)
        return call_success

    def subprocess_call(self, command):
        output = subprocess.check_output(command, shell=True)
        if not output:
            logger.error("Subprocess command failed")
            raise BackendFailedError(self.program, command)
        return output            

    def pull(self, image, tag):
        logger.debug("Pulling Docker image")
        pull_command = f'{self.program} pull {image}:{tag}'
        self.system_call(pull_command)

    def get_os_release(self, image, tag):
        logger.debug("Getting OS release of Docker image")
        container_command = 'cat /etc/os-release'
        run_command = f'{self.program} run {image}:{tag} {container_command}'
        system_command_output = self.subprocess_call(run_command)

        self.clean_up()

        logger.info("Parsing OS release information")
        os_release = self.parse_os_release(system_command_output)
        return os_release

    def clean_up(self):
        logger.debug('Stopping container')
        stop_container_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        self.system_call(stop_container_command)

        logger.debug('Removing container')
        remove_container_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        self.system_call(remove_container_command)

    def parse_os_release(self, system_command_output):
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')

        return os_release
