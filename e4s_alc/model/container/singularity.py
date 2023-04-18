import os
import re
import json
import atexit
import subprocess
from prettytable import PrettyTable
from datetime import datetime
from e4s_alc.model.container.podman import PodmanController
has_podman=False
try:
    import podman
    has_podman=True
except ImportError:
    pass
has_singularity=False
try:
    from spython.main import Client
    has_singularity=True
except ImportError:
    pass

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB']:
        if abs(size) < 1024.0 or unit == 'PiB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"

class SingularityController(PodmanController):
    def __init__(self):
        super(PodmanController, self).__init__('SingularityController')
        self.lacks_backend = False

        # Check if the python libraries are imported
        if not has_podman:
            print('Failed to find Podman python library')
            self.lacks_backend = True
        if not has_singularity:
            print('Failed to find Singularity python library')
            self.lacks_backend = True

        if self.lacks_backend:
            print("Missing package podman or spython: podman is also needed to manipulate singularity images with e4s-alc")
            return

        # Try to turn on API with podman 3
        try:
            server_process = subprocess.Popen(['podman', 'system', 'service', '-t', '0'])
            atexit.register(server_process.terminate)
        except:
            print('Failed to connect to podman API.')
            return

        # Try to connect with the docker runtime
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

        self.config_dir = os.path.join(os.path.expanduser('~'), '.e4s-alc')
        self.images_dir = os.path.join(self.config_dir, "singularity_images")
        self.tar_dir = os.path.join(self.config_dir, "podman_tarballs")

        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        if not os.path.exists(self.tar_dir):
            os.makedirs(self.tar_dir)


    def execute_build(self, name):
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
        container.commit(name)

        # Stop the running container
        container.stop()

        if not self.image_tag:
            self.image_tag = self.parse_image_name(self.image)[1]

        
        podmanSaveToTar = subprocess.Popen(['podman', 'save', '--format=oci-archive', '-o', self.tar_dir + '/' + name + '.tar', 'localhost/' + name]).wait()

        Client.build(recipe="oci-archive://" + self.tar_dir + '/' + name + ".tar", build_folder=self.images_dir, image= name + ".sif", sudo=False)

    def list_images(self, name=None, inter=False):
        contentIterator = os.scandir(self.images_dir)
        contentDict = {}
        for entry in contentIterator:
            if not entry.name.startswith('.') and entry.is_file():
                contentDict[entry.name] = entry.stat()
        self.show_images(contentDict)

    def show_images(self, image_dict):
        t = PrettyTable(['Name', 'Created', 'Size'])
        for image in image_dict:
            creation_date = datetime.fromtimestamp(image_dict.get(image).st_ctime).strftime("%m/%d/%Y, %H:%M:%S")
            t.add_row([image, creation_date, human_readable_size(image_dict.get(image).st_size)])
        print(t)

    def delete_image(self, name, force):
        image_path = self.images_dir + "/" + name
        try:
            os.remove(image_path)
        except FileNotFoundError as err:
            print("{} not found".format(image_path))
            raise SystemExit(err) from err
