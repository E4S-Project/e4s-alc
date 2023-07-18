import os
import configparser
from e4s_alc import logger, E4S_ALC_CONFIG_DIR

LOGGER = logger.get_logger(__name__)

class Model():
    def __init__(self, module_name):
        self.module_name = module_name
        self.config_dir = E4S_ALC_CONFIG_DIR
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
            config.read(self.config_file)
        if 'backend' not in config['DEFAULT']:
            self.create_configuration_file()
            config.read(self.config_file)

        backend = config.get('DEFAULT', 'backend')
        if backend == 'None':
            backend = None
        
        return backend

    def update_configuration_file(self, key, value):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        config.set('DEFAULT', key, value)
        with open(self.config_file, 'w') as f:
            config.write(f)

    def create_configuration_file(self):
        config = configparser.ConfigParser()
        config['DEFAULT'] = {'name': 'e4s-alc',
                             'backend': 'None'}

        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

        with open(self.config_file, 'w') as f:
            config.write(f)

    def set_backend(self, backend):
        self.update_configuration_file('backend', backend)
        LOGGER.info('Setting {} as backend!'.format(backend))
        return True

    def check_working_backend(self, backend, controller):
        if backend == 'docker':
            docker_controller = controller()
            if docker_controller.is_active:
                self.controller = docker_controller
                return True

        if backend == 'podman':
            podman_controller = controller()
            if podman_controller.is_active:
                self.controller = podman_controller
                return True

        if backend == 'singularity':
            singularity_controller = controller()
            if singularity_controller.is_active:
                self.controller = singularity_controller
                return True
        
        return False
