import os
import json

class Controller():
    def __init__(self, module_name):
        self.module_name = module_name
        self.client = None
        self.is_active = False
        self.image = None
        self.image_os = None
        self.image_tag = None
        self.image_id = None
        self.os_release = {}
        self.environment = {}
        self.commands = []
        self.mounts = []


    def read_args_file(self, file_path):
        abs_file_path = os.path.abspath(file_path)
        with open(abs_file_path, 'r') as json_file:
            data = json.load(json_file)
        return data

   
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


    def add_sles_package_commands(self, os_packages):
        # SLES packages needed for spack
        sles_packages = ' '.join([ 
            'curl', 'gzip', 'tar', 'python3', 'python3-pip', 'gcc',
            'gcc-c++', 'gcc-fortran', 'patch', 'make', 'gawk', 'xz',
            'cmake', 'bzip2', 'vim'
        ] + list(os_packages))

        # Add commands to install SLES packages
        self.commands.append('zypper update') 
        self.commands.append('zypper install -y {}'.format(sles_packages))


    def add_system_package_commands(self, os_packages):
        # Create a mapping from os specified -> packages required

        package_map = {
            'ubuntu': self.add_ubuntu_package_commands,
            'centos': self.add_centos_package_commands,
            'sles': self.add_sles_package_commands
        }
        package_map[self.os_release['ID']](os_packages) 


    def add_spack_package_commands(self, packages):
        # Create installation command for each package
        for package in packages:
            self.commands.append('spack install --yes-to-all {}'.format(package))

    def add_spack_environment_commands(self, file_path):
        # Create environment set up command with user-given yaml file
        self.commands.append('spack env create userenv {}'.format(file_path))
        self.commands.append('spack env activate userenv')
        self.commands.append('spack install')

    def install_spack(self):
        #TODO
        # Get correct version of spack progmatically
        SPACK_URL = 'https://github.com/spack/spack/releases/download/v0.19.1/spack-0.19.1.tar.gz'

        # Commands for downloading, unpacking, moving, and activating spack
        self.commands.append('curl -OL {}'.format(SPACK_URL))
        self.commands.append('gzip -d /spack-0.19.1.tar.gz')
        self.commands.append('tar -xf /spack-0.19.1.tar')
        self.commands.append('rm /spack-0.19.1.tar')
        self.commands.append('mv /spack-0.19.1 /spack')
        self.commands.append('. /spack/share/spack/setup-env.sh')
        self.commands.append('echo export PATH={}:/spack/bin >> ~/.bashrc'.format(self.environment['PATH']))


    def print_line(self):
        for i in range(os.get_terminal_size()[0]):
            print('=', end='')
