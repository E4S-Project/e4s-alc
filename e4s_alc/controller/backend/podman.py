import os
import subprocess
from e4s_alc.controller.backend import ContainerBackend
from e4s_alc.util import log_function_call, log_info, log_error, BackendFailedError

class PodmanBackend(ContainerBackend):
    """
    Podman backend class for handling podman container operations
    """

    @log_function_call
    def __init__(self):
        """
        Initialize PodmanBackend class with specific program name 'podman'
        """
        super().__init__()
        self.program = 'podman'

    @log_function_call
    def system_call(self, command):
        """
        Execute the given system command and raise an exception if it fails

        Args:
            command (str): The command to execute

        Returns:
            bool: True if command execution is successful
        """
        log_info(f"Executing command: {command}")
        call_success = not os.system(command)
        if not call_success:
            log_error(f"Command execution failed. Raising BackendFailedError for program: {self.program}")
            raise BackendFailedError(self.program, command)
        return call_success

    @log_function_call
    def subprocess_call(self, command):
        """
        Execute subprocess command and return its output

        Args:
            command (str): The command to execute

        Returns:
            str: Output of the command
        """
        log_info(f"Executing command: {command}")
        output = subprocess.check_output(command, shell=True)
        if not output:
            log_error(f"Command execution failed. Raising BackendFailedError for program: {self.program}")
            raise BackendFailedError(self.program, command)
        return output

    @log_function_call
    def pull(self, image, tag):
        """
        Pulls the podman image with given tag

        Args:
            image (str): Image name
            tag (str): Image tag
        """
        pull_command = f'{self.program} pull {image}:{tag}'
        self.system_call(pull_command)

    @log_function_call
    def get_os_release(self, image, tag):
        """
        Gets the OS release from a running Podman container and parses it

        Args:
            image (str): Image name
            tag (str): Image tag

        Returns:
            dict: Parsed OS release information
        """
        container_command = 'cat /etc/os-release'
        run_command = f'{self.program} run {image}:{tag} {container_command}'

        log_info("Executing subprocess command.")
        system_command_output = self.subprocess_call(run_command)

        log_info("Cleaning up.")
        self.clean_up()

        log_info("Parsing OS release.")
        os_release = self.parse_os_release(system_command_output)
        return os_release

    @log_function_call
    def clean_up(self):
        """
        Stops and removes the running Podman container
        """
        stop_container_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        log_info("Executing stop container command.")
        self.system_call(stop_container_command)

        remove_container_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        log_info("Executing remove container command.")
        self.system_call(remove_container_command)

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
