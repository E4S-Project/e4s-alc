import os
import subprocess
from e4s_alc.controller.backend import ContainerBackend
from e4s_alc.util import log_function_call, BackendFailedError

class DockerBackend(ContainerBackend):
    """
    Docker backend class for handling docker container operations
    """

    @log_function_call
    def __init__(self):
        """
        Initialize DockerBackend class with specific program name 'docker'
        """
        super().__init__()
        self.program = 'docker'

    @log_function_call
    def execute_system_command(self, command):
        """
        Execute the given system command and raise an exception if it fails

        Args:
            command (str): The command to execute

        Returns:
            bool: True if command execution is successful
        """
        call_success = not os.system(command)
        if not call_success:
            raise BackendFailedError(self.program, command)
        return call_success

    @log_function_call
    def execute_subprocess_command(self, command):
        """
        Execute subprocess command and return its output

        Args:
            command (str): The command to execute

        Returns:
            str: Output of the command
        """
        output = subprocess.check_output(command, shell=True)
        if not output:
            raise BackendFailedError(self.program, command)
        return output

    @log_function_call
    def pull(self, image, tag):
        """
        Pulls the docker image with given tag

        Args:
            image (str): Image name
            tag (str): Image tag
        """
        pull_command = f'{self.program} pull {image}:{tag}'
        self.execute_system_command(pull_command)

    @log_function_call
    def get_os_release(self, image, tag):
        """
        Gets the OS release from a running Docker container and parses it

        Args:
            image (str): Image name
            tag (str): Image tag

        Returns:
            dict: Parsed OS release information
        """
        container_command = 'cat /etc/os-release'
        run_command = f'{self.program} run {image}:{tag} {container_command}'
        system_command_output = self.execute_subprocess_command(run_command)

        self.clean_up()

        os_release = self.parse_os_release(system_command_output)
        return os_release

    @log_function_call
    def clean_up(self):
        """
        Stops and removes the running Docker container
        """
        stop_container_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        self.execute_system_command(stop_container_command)

        remove_container_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        self.execute_system_command(remove_container_command)

    @log_function_call
    def parse_os_release(self, system_command_output):
        """
        Parses the OS release information from system command output

        Args:
            system_command_output (str): System command output

        Returns:
            dict: Parsed OS release information
        """
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')

        return os_release
