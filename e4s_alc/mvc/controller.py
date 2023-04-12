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
