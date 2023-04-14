import os
import json
from prettytable import PrettyTable
from datetime import datetime
from e4s_alc.mvc.controller import Controller
has_docker=False
try:
    import docker
    has_docker=True
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

class SingularityController(Controller):
    def __init__(self):
        super().__init__('SingularityController')
        self.lacks_backend = False

        # Check if the python libraries are imported
        if not has_docker:
            print('Failed to find Docker python library')
            self.lacks_backend = True
        if not has_singularity:
            print('Failed to find Singularity python library')
            self.lacks_backend = True

        if self.lacks_backend:
            print("Missing package docker or spython: docker is also needed to manipulate singularity images with e4s-alc")
            return

        # Try to connect with the docker runtime
        try:
            self.client = docker.from_env(timeout=600)
        except docker.errors.DockerException:
            print('Failed to connect to Docker client')
            return
        
        self.is_active = True

        self.config_dir = os.path.join(os.path.expanduser('~'), '.e4s-alc')
        self.images_dir = os.path.join(self.config_dir, "singularity_images")

        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)


    def read_args_file(self, file_path):
        abs_file_path = os.path.abspath(file_path)
        with open(abs_file_path, 'r') as json_file:
            data = json.load(json_file)

        return data

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
        self.image_os, self.image_tag = self.parse_image_name(image)

        # Try to pull the image if it exists
        try:
            self.client.images.pull(self.image_os, self.image_tag)
        except docker.errors.ImageNotFound:
            print('Image was not found.')
            exit(1)


    def find_image(self, image):
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


    def init_image(self, image):
        # Pull image
        self.pull_image(image)

        # Parse image os release
        self.parse_os_release()

        # Parse the existing environment of the image
        self.parse_environment()


    def read_image(self, image):
        # Find image
        self.find_image(image)

        # Parse image os release
        self.parse_os_release()

        # Parse the existing environment of the image
        self.parse_environment()


    def mount_and_copy(self, host_path, image_path):
        # Get absolutely path of host directory
        abs_host_path = os.path.abspath(host_path)
        if image_path[0] != '/':
            image_path = '/' + image_path

        # Add items to mount list
        mount_item = '{}:/tmp{}'.format(abs_host_path, image_path)
        self.mounts.append(mount_item)

        # Add command to copy directory from mounted volume to image
        self.commands.append('cp -r /tmp{} {}'.format(image_path, image_path))

    
    def expand_tarball(self, host_path, image_path):
        abs_host_path = os.path.abspath(host_path)
        if image_path[0] != '/':
            image_path = '/' + image_path

        # Add items to mount list
        host_body, file_tail = os.path.split(abs_host_path)
        host_body_parent, host_body_dir =  os.path.split(host_body)
        mount_item = '{}:/tmp/{}'.format(host_body, host_body_dir)
        self.mounts.append(mount_item)

        # Add command to open the tarball into the specified path
        self.commands.append('tar xf /tmp/{}/{} -C {}'.format(host_body_dir, file_tail, image_path))

    def add_ubuntu_package_commands(self, os_packages):
        # Ubuntu packages needed for spack
        ubuntu_packages = ' '.join([
            'build-essential', 'ca-certificates', 'coreutils', 'curl', 
            'environment-modules', 'gfortran', 'git', 'gpg', 'lsb-release', 'vim', 
            'python3', 'python3-distutils', 'python3-venv', 'unzip', 'zip', 'cmake' 
        ] + list(os_packages))

        # Add commands to install Ubuntu packages
        self.commands.append('apt-get update')
        self.commands.append('apt-get install -y {}'.format(ubuntu_packages))


    def add_centos_package_commands(self, os_packages):
        # Centos packages needed for spack
        centos_packages = ' '.join([
            'curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim'
        ] + list(os_packages))

        # If Centos is version, add commands to change repos
        if self.os_release['VERSION'] == '8':
            swap_repo = 'swap centos-linux-repos centos-stream-repos'
            self.commands.append('yum -y --disablerepo \'*\' --enablerepo=extras {}'.format(swap_repo))
            self.commands.append('yum -y distro-sync')
        
        # Add commands to install Centos packages
        self.commands.append('yum update -y')
        self.commands.append('yum install epel-release -y')
        self.commands.append('yum --enablerepo epel groupinstall -y "Development Tools"')
        self.commands.append('yum --enablerepo epel install -y {}'.format(centos_packages))
        self.commands.append('python3 -m pip install boto3')


    def add_system_package_commands(self, os_packages):
        # Create a mapping from os specified -> packages required
        package_map = {
            'ubuntu': self.add_ubuntu_package_commands,
            'centos': self.add_centos_package_commands
        }
        package_map[self.os_release['ID']](os_packages) 


    def install_spack(self):
        #TODO
        # Get correct version of spack progmatically
        SPACK_URL = 'https://github.com/spack/spack/releases/download/v0.19.1/spack-0.19.1.tar.gz'

        # Commands for downloading, unpacking, moving, and activating spack
        self.commands.append('curl -OL {}'.format(SPACK_URL)) 
        self.commands.append('gunzip /spack-0.19.1.tar.gz')
        self.commands.append('tar -xf /spack-0.19.1.tar')
        self.commands.append('rm /spack-0.19.1.tar')
        self.commands.append('mv /spack-0.19.1 /spack')
        self.commands.append('. /spack/share/spack/setup-env.sh')
        self.commands.append('echo export PATH={}:/spack/bin >> ~/.bashrc'.format(self.environment['PATH']))


    def add_spack_package_commands(self, packages):
        # Create installation command for each package
        for package in packages:
            self.commands.append('spack install {}'.format(package))

    def print_line(self):
        for i in range(os.get_terminal_size()[0]):
            print('=', end='')

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

                # Print to screen
                print()
                for chunk in stream:
                    print(chunk.decode().strip())
                print()

        except:
            print('Stopping container...')
            container.stop()
            exit(1)

        # Commit new image
        container.commit(name)

        # Stop the running container
        container.stop()

        if not self.image_tag:
            self.image_tag = self.parse_image_name(self.image)[1]
        Client.build(recipe="docker-daemon://" + name + ":" + self.image_tag, build_folder=self.images_dir, image= name + ".sif", sudo=False)

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