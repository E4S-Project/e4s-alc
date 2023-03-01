import os
from e4s_alc.mvc.controller import Controller

class DockerController(Controller):
    def __init__(self):
        super().__init__('DockerController')

        try:
            import docker
        except ImportError:
            print('Error: failed to find Docker python library')
            return

        try:
            self.client = docker.from_env(timeout=600)
        except docker.errors.DockerException:
            print('Error: failed to connect to Docker client')
            return
        
        self.is_active = True
        self.image = None
        self.image_os = None
        self.image_tag = None
        self.os_release = {}
        self.environment = {}
        self.commands = []
        self.mounts = []

    def pull_image(self, image):
        import docker
        self.image = image

        if ':' in self.image:
            image_chunks = self.image.split(':')
            if len(image_chunks) != 2:
                print('Error processing image \'{}\'.'.format(self.image))
            self.image_os, self.image_tag = image_chunks
        else:
            self.image_os, self.image_tag = self.image, 'latest'

        try:
            self.client.images.pull(self.image_os, self.image_tag)
        except docker.errors.ImageNotFound:
            print('Image was not found.')
            exit(1)

    def parse_os_release(self):
        os_release_raw = self.client.containers.run(self.image, 'cat /etc/os-release', remove=True)
        os_release_parsed = os_release_raw.decode().replace('\"', '').splitlines()
        for item in os_release_parsed:
            if item == '':
                continue
            item_name, item_value = item.split('=')
            self.os_release[item_name] = item_value

    def parse_environment(self):
        environment_raw = self.client.containers.run(self.image, 'printenv', remove=True)
        environment_parsed = environment_raw.decode().replace('\"', '').splitlines()
        for item in environment_parsed:
            item_name, item_value = item.split('=')
            self.environment[item_name] = item_value


    def add_ubuntu_package_commands(self, os_packages):
        ubuntu_packages = ' '.join([ 
            'build-essential', 'ca-certificates', 'coreutils', 'curl', 
            'environment-modules', 'gfortran', 'git', 'gpg', 'lsb-release', 'vim', 
            'python3', 'python3-distutils', 'python3-venv', 'unzip', 'zip', 'cmake' 
        ] + list(os_packages)) 
        self.commands.append('apt-get update') 
        self.commands.append('apt-get install -y {}'.format(ubuntu_packages))

    
    def add_centos_package_commands(self, os_packages):
        centos_packages = ' '.join([
            'curl', 'findutils', 'gcc-c++', 'gcc', 'gcc-gfortran', 'git',  
            'gnupg2', 'hostname', 'iproute', 'redhat-lsb-core', 'make', 'patch',
            'python3', 'python3-pip', 'python3-setuptools', 'unzip', 'cmake', 'vim'
        ] + list(os_packages))

        if self.os_release['VERSION'] == '8':
            swap_repo = 'swap centos-linux-repos centos-stream-repos'
            self.commands.append('yum -y --disablerepo \'*\' --enablerepo=extras {}'.format(swap_repo))
            self.commands.append('yum -y distro-sync')
        
        self.commands.append('yum update -y')
        self.commands.append('yum install epel-release -y')
        self.commands.append('yum --enablerepo epel groupinstall -y "Development Tools"')
        self.commands.append('yum --enablerepo epel install -y {}'.format(centos_packages))
        self.commands.append('python3 -m pip install boto3')

    def init_image(self, image):
        self.pull_image(image)
        self.parse_os_release()
        self.parse_environment()

    def mount_and_copy(self, host_path, image_path):
        abs_host_path = os.path.abspath(host_path)
        if image_path[0] != '/':
            image_path = '/' + image_path
        mount_item = '{}:/tmp{}'.format(abs_host_path, image_path)
        self.mounts.append(mount_item)
        self.commands.append('cp -r /tmp{} {}'.format(image_path, image_path))

    def add_system_package_commands(self, os_packages):
        package_map = {
            'ubuntu': self.add_ubuntu_package_commands,
            'centos': self.add_centos_package_commands
        }
        package_map[self.os_release['ID']](os_packages) 


    def add_spack_package_commands(self, packages):
        # GET SPACK VERSION
        SPACK_URL = 'https://github.com/spack/spack/releases/download/v0.19.1/spack-0.19.1.tar.gz'
        self.commands.append('curl -OL {}'.format(SPACK_URL)) 
        self.commands.append('gunzip /spack-0.19.1.tar.gz')
        self.commands.append('tar -xvf /spack-0.19.1.tar')
        self.commands.append('rm /spack-0.19.1.tar')
        self.commands.append('mv /spack-0.19.1 /spack')
        self.commands.append('. /spack/share/spack/setup-env.sh')
        self.commands.append('echo export PATH={}:/spack/bin >> ~/.bashrc'.format(self.environment['PATH']))

        for package in packages:
            self.commands.append('spack install {}'.format(package))

    def execute_build(self, name):
        env = {
            'PYTHONUNBUFFERED': '1',
            'DEBIAN_FRONTEND': 'noninteractive',
            'PATH': '{}:/spack/bin'.format(self.environment['PATH'])
        }

        container = self.client.containers.run(self.image, detach=True, tty=True, volumes=self.mounts)

        for command in self.commands:
            print('=' * 90)
            print('Command: ', command)
            print('=' * 90)

            rv, stream = container.exec_run(
                'bash -c \"{}\"'.format(command),
                stream=True,
                environment=env
            )

            print()
            for chunk in stream:
                print(chunk.decode().strip())
            print()

        # Commit new image
        container.commit(name)
        container.stop()

