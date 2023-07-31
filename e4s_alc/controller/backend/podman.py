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

    def system_call(self, command):
        call_success = not os.system(command)
        if not call_success:
            logger.error("System call failed")
            raise BackendFailedError(self.program, command)
        return call_success

    def subprocess_call(self, command):
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            logger.error("Subprocess call failed")
            raise BackendFailedError(self.program, command) from e
        return output

    def pull(self, image, tag):
        logger.debug("Pulling image")
        pull_command = f'{self.program} pull {image}:{tag}'
        self.system_call(pull_command)

    def get_os_release(self, image, tag):
        logger.debug("Getting OS release of Podman image")
        container_command = 'cat /etc/os-release'
        run_command = f'{self.program} run {image}:{tag} {container_command}'
        system_command_output = self.subprocess_call(run_command)

        self.clean_up()

        os_release = self.parse_os_release(system_command_output)
        return os_release

    def clean_up(self):
        logger.debug('Stopping container')
        stop_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        self.system_call(stop_command)

        logger.debug('Removing container')
        remove_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        self.system_call(remove_command)

    def parse_os_release(self, system_command_output):
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')
            
        return os_release
