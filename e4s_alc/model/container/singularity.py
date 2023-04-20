import os
import re
import json
import atexit
import subprocess
from prettytable import PrettyTable
from datetime import datetime
from e4s_alc.model.container.podman import PodmanController
from e4s_alc.model.container.docker import DockerController
from e4s_alc.mvc.controller import Controller

has_docker=False
try:
    import docker
    has_docker=True
except ImportError:
    pass
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

class SingularityController(PodmanController, DockerController):
    def __init__(self):
        Controller.__init__(self, 'SingularityController')
        self.lacks_backend = False
        self.use_docker = True
        self.use_podman = True

        # Check if the python libraries are imported
        if not has_docker or not has_podman:
            print('Failed to find Podman or Docker python library')
            self.lacks_backend = True
        if not has_singularity:
            print('Failed to find Singularity python library')
            self.lacks_backend = True

        if self.lacks_backend:
            print("Missing package podman, docker or spython: either one of podman and docker is also needed to manipulate singularity images with e4s-alc")
            return

        # Try to turn on API with podman 3
        try:
            server_process = subprocess.Popen(['podman', 'system', 'service', '-t', '0'])
            atexit.register(server_process.terminate)
        except:
            print('Failed to connect to podman API.')

        # Try to connect with the podman runtime
        try:
            process = subprocess.Popen(['podman', 'info', '--format', 'json'],
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
            process_out, process_err = process.communicate()
            if process_err:
                print('Failed to connect to Podman client')


            process_out_dict = json.loads(process_out.decode('utf-8'))
            uri = 'unix://{}'.format(process_out_dict['host']['remoteSocket']['path'])

            self.client_podman = podman.PodmanClient(base_url=uri)
        except podman.errors.exceptions.APIError:
            print('Failed to connect to Podman client')
            self.use_podman = False

        # Try to connect with the docker runtime     
        try:
            self.client_docker = docker.from_env(timeout=600)
        except docker.errors.DockerException:
            print('Failed to connect to Docker client') 
            self.use_docker = False
        
        if not self.use_docker and not self.use_podman:
            return

        self.is_active = True

        print("Podman is available: {}".format(self.use_podman))
        print("Docker is available: {}".format(self.use_docker))

        self.config_dir = os.path.join(os.path.expanduser('~'), '.e4s-alc')
        self.images_dir = os.path.join(self.config_dir, "singularity_images")
        self.tar_dir = os.path.join(self.config_dir, "podman_tarballs")

        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)

        if not os.path.exists(self.tar_dir):
            os.makedirs(self.tar_dir)

    def set_parent(self, arg_parent):
        if arg_parent == "docker":
            self.parent = DockerController
            self.client = self.client_docker
        else:
            self.parent = PodmanController
            self.client = self.client_podman

    
    def read_image(self, image):
        self.parent.find_image(self, image)
        
        self.parent.parse_os_release(self)
        
        self.parent.parse_environment(self)


    def init_image(self, image):
        self.parent.pull_image(self, image)
        
        self.parent.parse_os_release(self)
        
        self.parent.parse_environment(self)


    def execute_build(self, name):
        self.parent.execute_build(self, name)

        # Build the singularity image
        self.build_to_sif(name)


    def build_to_sif(self, name):
        if not self.image_tag:
            self.image_tag = self.parse_image_name(self.image)[1]
        if self.parent == DockerController:
            Client.build(recipe="docker-daemon://" + name + ":" + self.image_tag, build_folder=self.images_dir, image= name + ".sif", sudo=False)
        else:
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
