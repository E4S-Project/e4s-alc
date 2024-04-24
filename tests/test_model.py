import sys
import unittest
import argparse
from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
from e4s_alc.cli.commands.create import CreateCommand
from e4s_alc.model.model import Model

import types
from subprocess import Popen, PIPE

import logging
logger = logging.getLogger('core')

class ModelTests(unittest.TestCase):
#    def setUp(self):
#
    def test_read_backend_conf(self):
        parser = argparse.ArgumentParser()
        subparsers = parser.add_subparsers(dest='command')
        result = CreateCommand().create_subparser(subparsers)
        args = parser.parse_args()
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
