import os
import re
import json
import atexit
import subprocess
import requests
from prettytable import PrettyTable
from datetime import datetime
from e4s_alc.mvc.controller import Controller

has_podman=False
try:
    import podman
    has_podman=True
except ImportError:
    pass

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if abs(size) < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

class PodmanController(Controller):
    def __init__(self):
        super().__init__('PodmanController')

        # Try to import podman
        if not has_podman:
            print('Failed to find Podman python library')
            return

        # Try to turn on API with podman 3
        try:
            server_process = subprocess.Popen(['podman', 'system', 'service', '-t', '0'])
            atexit.register(server_process.terminate)
        except:
            print('Failed to connect to podman API.')
            return

        # Try to connect to podman client
        try:
            process = subprocess.Popen(['podman', 'info', '--format', 'json'],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            process_out, process_err = process.communicate()
            if process_err:
                print('Failed to connect to Podman client')
                return

            process_out_dict = json.loads(process_out.decode('utf-8'))
            uri = 'unix://{}'.format(process_out_dict['host']['remoteSocket']['path'])

            self.client = podman.PodmanClient(base_url=uri)
        except podman.errors.exceptions.APIError:
            print('Failed to connect to Podman client')
            return
        
        self.is_active = True

    def parse_image_name(self, image):
        if ':' in self.image:
            image_chunks = self.image.split(':')
            if len(image_chunks) != 2:
                print('Error processing image \'{}\'.'.format(self.image))
            self.image_os, self.image_tag = image_chunks
        else:
            self.image_os, self.image_tag = self.image, 'latest'
        return self.image_os, self.image_tag

    def pull_image(self, image):
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
            image_data = self.client.images.pull(self.image_os, self.image_tag)
            self.image = image_data.attrs['RepoTags'][0]
        except podman.errors.ImageNotFound:
            print('Image was not found.')
            exit(1)
        except podman.errors.NotFound:
            print('Image was not found.')
            exit(1)

    def find_image(self, image):
        self.image = image

        # Try to get image from client
        try:
            self.client.images.get(image)
        except podman.errors.ImageNotFound:
            print('Image was not found.')
            exit(1)

    def parse_os_release(self):
        # Run the image and execute cat command to read os release
        container = self.client.containers.run(self.image, ['cat', '/etc/os-release'], remove=True, detach=True)
        os_release_gen = container.logs()

        os_release_raw = b''
        for line in os_release_gen:
            os_release_raw += line + b'\n'

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
        container = self.client.containers.run(self.image, ['printenv'], remove=True, detach=True)
        environment_gen = container.logs()

        environment_raw = b''
        for line in environment_gen:
            environment_raw += line + b'\n'

        # Parse the response from the container
        environment_parsed = environment_raw.decode().replace('\"', '').splitlines()

        # Iterate through each item of the environment
        for item in environment_parsed:

            # Add key, value pair to class dictionary
            item_name, item_value = item.split('=')
            self.environment[item_name] = item_value


    def init_image(self, image):
        # Pull image
        self.pull_image(image)

        # Parse image os release
        self.parse_os_release()

        # Parse the existing environment of the image
        self.parse_environment()


    def execute_build(self, name, changes=None):
        # Create environment for container
        env = {
            'PYTHONUNBUFFERED': '1',
            'DEBIAN_FRONTEND': 'noninteractive',
            'PATH': '{}:/spack/bin'.format(self.environment['PATH'])
        }

        mounts = []
        for mount in self.mounts:
            mount_src, mount_dest = mount.split(':')
            mount = {
                'type': 'bind',
                'source': mount_src,
                'target': mount_dest,
                'read_only': True
            }
            mounts.append(mount)

        # Create a running detached container
        container = self.client.containers.run(self.image, detach=True, tty=True, mounts=mounts)

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
                    print(chr(chunk), end='') 

                print()

        except Exception as e:
            raise e
            print(e)
            print('Stopping container...')
            container.stop()
            exit(1)

        # Commit new image
        container.commit(name, changes=changes)

        # Stop the running container
        container.stop()
    

    def list_images(self, name=None, inter=False):
        images = self.client.images.list(name=name, all=inter)
        self.show_images(images)

    def show_images(self, image_list):
        t = PrettyTable(['Name', 'Tag', 'Id', 'Created', 'Size'])
        for image in image_list:
            if image.tags:
                image_name, image_tag = image.tags[0].split(':')
            else:
                image_name, image_tag = "<none>", "<none>"
            creation_date = datetime.fromtimestamp(image.attrs.get('Created')).strftime("%m/%d/%Y, %H:%M:%S")
            t.add_row([image_name, image_tag, image.short_id, creation_date, human_readable_size(image.attrs.get('Size'))])
        print(t)
    
    def delete_image(self, names, force):
        try:
            for name in names:
                self.client.images.remove(name, force=force)
        except requests.exceptions.HTTPError as err:
            error_string = "Image deletion has failed:"
            error_code = err.response.status_code
            if error_code == 404:
                error_string += " image not found with name {}.".format(name)
            elif 409:
                error_string += " image {} used by container. Use '-f' to force remove, or remove container using 'alc delete -c $CONTAINER_ID'.".format(name)
            print(error_string)
            raise SystemExit(err) from err

    def delete_container(self, ID, force):
        try:
            current = self.client.containers.get(ID)
            current.remove(force=force)
        except podman.errors.APIError as err:
            error_string = "Container deletion has failed:"
            print(error_string)
            raise SystemExit(err) from err

    def prune_containers(self):
        entered_value = input("WARNING: All stopped containers will be deleted, are you sure you want to proceed?[y/N]\n")
        if entered_value in ['y', 'Y', 'yes']:
            try:
                deleted = self.client.containers.prune()
            except podman.errors.APIError as err:
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
