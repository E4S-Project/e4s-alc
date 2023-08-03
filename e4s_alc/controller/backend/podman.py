import os
import logging
import subprocess
from e4s_alc.controller.backend import ContainerBackend
from e4s_alc.util import log_function_call, BackendFailedError

class PodmanBackend(ContainerBackend):
    """A class to interact with the Podman container backend."""

    @log_function_call
    def __init__(self):
        """
        Initializer of the PodmanBackend class.
        This sets the 'program' attribute to 'podman'.
        """
        super().__init__()
        self.program = 'podman'

    @log_function_call
    def system_call(self, command):
        """
        Executes a system command and throws a
        BackendFailedError if the command fails.

        Args:
            command (str): The command to execute.

        Returns:
            bool: True if the command executed successfully. Else, False.
        """
        call_success = not os.system(command)
        if not call_success:
            raise BackendFailedError(self.program, command)
        return call_success

    @log_function_call
    def subprocess_call(self, command):
        """
        Executes a command using subprocess and returns output.
        If command execution fails, raises a BackendFailedError.

        Args:
            command (str): The command to execute.

        Returns:
            bytes: The output of the command execution.

        Raises:
            BackendFailedError: If the command execution throws a CalledProcessError.
        """
        try:
            output = subprocess.check_output(command, shell=True)
        except subprocess.CalledProcessError as e:
            raise BackendFailedError(self.program, command) from e
        return output

    @log_function_call
    def pull(self, image, tag):
        """
        Pull an image from a repository using podman.

        Args:
            image (str): The name of the image.
            tag (str): The tag/version of the image.
        """
        pull_command = f'{self.program} pull {image}:{tag}'
        self.system_call(pull_command)

    @log_function_call
    def get_os_release(self, image, tag):
        """
        Get the OS release information from an image.

        Args:
            image (str): The name of the image.
            tag (str): The tag/version of the image.

        Returns:
            dict: Dictionary containing key-value pairs of OS information.
        """
        container_command = 'cat /etc/os-release'
        run_command = f'{self.program} run {image}:{tag} {container_command}'
        system_command_output = self.subprocess_call(run_command)

        self.clean_up()

        os_release = self.parse_os_release(system_command_output)
        return os_release

    @log_function_call
    def clean_up(self):
        """
        Cleans up the environment after executing podman instructions.
        Stops and removes the last created podman container.
        """
        stop_command = f'{self.program} stop $({self.program} ps -l -q) &> /dev/null'
        self.system_call(stop_command)

        remove_command = f'{self.program} rm $({self.program} ps -l -q) &> /dev/null'
        self.system_call(remove_command)

    @log_function_call
    def parse_os_release(self, system_command_output):
        """
        Parses the output of 'cat /etc/os-release' command
        into a dictionary.

        Args:
            system_command_output (bytes): Output from the system command.

        Returns:
            dict: A dictionary containing OS information.
        """
        os_release = {}
        os_release_list = system_command_output.decode('utf-8').split('\n')
        for item in os_release_list:
            if not item:
                continue
            key, value = item.split('=')
            os_release[key] = value.replace('"', '')

        return os_release
