import os
import re
import json
from e4s_alc.mvc.controller import Controller

class DockerController(Controller):
    def __init__(self):
        super().__init__('DockerController')

        # Try to import the python library
        try:
            import docker
        except ImportError:
            print('Failed to find Docker python library')
            return

        # Try to connect with the docker runtime
        try:
            self.client = docker.from_env(timeout=600)
        except docker.errors.DockerException:
            print('Failed to connect to Docker client')
            return
        
        self.is_active = True

    def pull_image(self, image):
        import docker
        self.image = image

        # Parse the image and tag
        if ':' in self.image:
            image_chunks = self.image.split(':')
            if len(image_chunks) != 2:
                print('Error processing image \'{}\'.'.format(self.image))
            self.image_os, self.image_tag = image_chunks
        else:
            self.image_os, self.image_tag = self.image, 'latest'

        # Try to pull the image if it exists
        try:
            self.client.images.pull(self.image_os, self.image_tag)
        except docker.errors.ImageNotFound:
            print('Image was not found.')
            exit(1)
        except docker.errors.NotFound:
            print('Image was not found.')
            exit(1)

    def find_image(self, image):
        import docker
        self.image = image

        # Try to get image from client
        try:
            self.client.images.get(image)
        except docker.errors.ImageNotFound:
            print('Image was not found.')
            exit(1)


    def parse_os_release(self):
        # Run the image and execute cat command to read os release
        os_release_raw = self.client.containers.run(self.image, 'cat /etc/os-release', remove=True)

        # Parse the response from the container
        os_release_parsed = os_release_raw.decode().replace('\"', '').splitlines()

        # Iterate through each item of os release
        for item in os_release_parsed:

            # Ignore blank items
            if item == '':
                continue

            # Add key, value pair to class dictionary
            item_name, item_value = item.split('=')
            self.os_release[item_name] = item_value


    def parse_environment(self):
        # Run the image and execute printenv to read existing environment
        environment_raw = self.client.containers.run(self.image, 'printenv', remove=True)

        # Parse the response from the container
        environment_parsed = environment_raw.decode().replace('\"', '').splitlines()

        # Iterate through each item of the environment
        for item in environment_parsed:

            # Add key, value pair to class dictionary
            item_name, item_value = item.split('=')
            self.environment[item_name] = item_value

    
    def execute_build(self, name):
        # Create environment for container
        env = {
            'PYTHONUNBUFFERED': '1',
            'DEBIAN_FRONTEND': 'noninteractive',
            'PATH': '{}:/spack/bin'.format(self.environment['PATH'])
        }

        # Create a running detached container
        container = self.client.containers.run(self.image, detach=True, tty=True, volumes=self.mounts)

        try:
            # Iterate through each command and execute
            for command in self.commands:
                self.print_line()
                print('Command: ', command)
                self.print_line()

                # Execute
                rv, stream = container.exec_run(
                    'bash -c \"{}\"'.format(command),
                    stream=True,
                    environment=env
                )

                # Create capture group for printing output.
                # In the future, a printing module will be used.
                pattern = re.compile(r"(\[|\[\.+|\.)$")

                # Print to screen
                print()
                for chunk in stream:
                    output = chunk.decode().strip()
                    matches = pattern.findall(output)

                    if matches:
                        print(output, end='')
                    else:
                        print(output)
                print()

        except:
            print('Stopping container...')
            container.stop()
            exit(1)

        # Commit new image
        container.commit(name)

        # Stop the running container
        container.stop()
