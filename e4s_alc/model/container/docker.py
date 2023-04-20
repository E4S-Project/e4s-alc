import os
import re
import json
from prettytable import PrettyTable
from dateutil import parser
import requests
from e4s_alc.mvc.controller import Controller

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if abs(size) < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

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

    def list_images(self, name=None, inter=False):
        import docker
        try:
            images = self.client.images.list(name, all=inter)
        except docker.errors.APIError as err:
            error_string = "Image listing has failed:"
            print(error_string)
            raise SystemExit(err) from err
        self.show_images(images)

    def show_images(self, image_list):
        t = PrettyTable(['Name', 'Tag', 'Id', 'Created', 'Size'])
        for image in image_list:
            if image.tags:
                image_name, image_tag = image.tags[0].split(':')
            else:
                image_name, image_tag = "<none>", "<none>"
            short_id = image.short_id.split(':')[1]
            creation_date = parser.parse(image.attrs.get('Created'))
            t.add_row([image_name, image_tag, short_id, creation_date.strftime("%m/%d/%Y, %H:%M:%S"), human_readable_size(image.attrs.get('Size'))])
        print(t)
    
    def prune_images(self):
        import docker
        entered_value = input("WARNING: All dangling images will be deleted, are you sure you want to proceed?[y/N]\n")
        if entered_value in ['y', 'Y', 'yes']:
            try:
                deleted = self.client.images.prune(filters={'dangling':True})
            except docker.errors.APIError as err:
                raise SystemExit(err) from err
            if not deleted["ImagesDeleted"]:
                print("No images were deleted: no unused images found.\nAre the corresponding stopped containers removed?\nConsider using 'e4s-alc delete -c $CONTAINER_ID' or 'e4s-alc delete --prune-containers'.")
            else:
                self.print_line()
                print("Pruned images:\n")
                for item in deleted['ImagesDeleted']:
                    print(item['Deleted'])
                print("\nSpace Reclaimed:\n")
                print(human_readable_size(deleted['SpaceReclaimed']))

    def prune_containers(self):
        import docker
        entered_value = input("WARNING: All stopped containers will be deleted, are you sure you want to proceed?[y/N]\n")
        if entered_value in ['y', 'Y', 'yes']:
            try:
                deleted = self.client.containers.prune()
            except docker.errors.APIError as err:
                raise SystemExit(err) from err
            if not deleted["ContainersDeleted"]:
                print("No containers were deleted: no stopped containers found.")
            else:
                self.print_line()
                print("Pruned containers:\n")
                for item in deleted['ContainersDeleted']:
                    print(item)
                print("\nSpace Reclaimed:")
                print(human_readable_size(deleted['SpaceReclaimed'], 2))
                self.print_line()

    def delete_image(self, name, force):
        try:
            self.client.images.remove(name, force=force)
        except requests.exceptions.HTTPError as err:
            error_string = "Image deletion has failed:"
            error_code = err.response.status_code
            if error_code == 404:
                error_string += " image not found with name."
            elif 409:
                error_string += " image used by container. Use '-f' to force remove, or remove container using 'alc detele -c $CONTAINER_ID'."
            print(error_string)
            raise SystemExit(err) from err

    def delete_container(self, ID, force):
        import docker
        try:
            current = self.client.containers.get(ID)
            current.remove(force=force)
        except docker.errors.APIError as err:
            error_string = "Container deletion has failed:"
            print(error_string)
            raise SystemExit(err) from err
