import os
import configparser

class Model():
    def __init__(self, module_name):
        self.module_name = module_name
        self.config_dir = os.path.join(os.path.expanduser('~'), '.e4s-alc')
        self.config_file_name = 'config.ini'
        self.config_file = os.path.join(self.config_dir, self.config_file_name)
        self.backend = self.read_backend_configuration()
        self.controller = None

    def read_backend_configuration(self):
        if not os.path.exists(self.config_file):
            self.create_configuration_file()

        config = configparser.ConfigParser()
        config.read(self.config_file)
        if 'DEFAULT' not in config:
            self.create_configuration_file()
        if 'backend' not in config['DEFAULT']:
            self.create_configuration_file()

        self.backend = config.get('DEFAULT', 'backend')
        if self.backend == 'None':
            self.backend = None

    def update_configuration_file(self, key, value):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        config.set('DEFAULT', key, value)
        with open(self.config_file, 'w') as f:
            config.write(f)

    def create_configuration_file(self):
        # Write configuration to file
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'name': 'e4s-alc',
                             'backend': 'None'}

        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        with open(self.config_file, 'w') as f:
            config.write(f)

    def set_backend(self, backend):
        self.update_configuration_file('backend', backend)
        return True

    def check_working_backend(self, backend, controller):
        # Check if the backend is working

        if backend == 'docker':
            docker_controller = controller()
            if docker_controller.is_active:
                self.controller = docker_controller
                self.set_backend(backend)
                return True
            else:
                return False

        if backend == 'podman':
            podman_controller = controller()
            if podman_controller.is_active:
                self.controller = podman_controller
                self.set_backend(backend)
                return True
            else:
                return False
