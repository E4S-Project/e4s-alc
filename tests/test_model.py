import unittest
import os
from e4s_alc.mvc.model import Model
from e4s_alc import logger, E4S_ALC_HOME

logger.set_log_level("FATAL")

ASSETS_DIRECTORY = E4S_ALC_HOME + "/tests/assets/"

class ModelTests(unittest.TestCase):

    def test_read_backend_conf(self):
        model = Model("test")
        model.config_file = ASSETS_DIRECTORY + "config.ini"
        self.assertEqual(model.read_backend_configuration(), "singularity")

    def test_read_backend_conf_empty(self):
        model = Model("test")
        model.config_dir = ASSETS_DIRECTORY
        model.config_file_name = "config_empty.ini"
        model.config_file = ASSETS_DIRECTORY + "config_empty.ini"
        read_backend = model.read_backend_configuration()
        self.assertEqual(read_backend, None)
        open(model.config_file, 'w').close()
    
    def test_read_backend_no_conf(self):
        model = Model("test")
        model.config_dir = ASSETS_DIRECTORY
        model.config_file_name = "config_nofile.ini"
        model.config_file = ASSETS_DIRECTORY + "config_nofile.ini"
        model.create_configuration_file()
        self.assertEqual(os.path.exists(model.config_file), True)
        os.remove(model.config_file)

    def test_modify_backend_conf(self):
        model = Model("test")
        model.config_file = ASSETS_DIRECTORY + "config_modify.ini"
        model.set_backend("docker")
        self.assertEqual(model.read_backend_configuration(), "docker")
        model.set_backend("singularity")
        self.assertEqual(model.read_backend_configuration(), "singularity")
