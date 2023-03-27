import sys
import unittest
from unittest.mock import patch
from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
from e4s_alc.model.container.docker import DockerController
import e4s_alc

import docker

class CreateTests(unittest.TestCase):
    def test_create_empty_image(self):
        with self.assertRaises(SystemExit) as system_exit:
            cli_main_cmd.main(['create'])

    @unittest.skipIf('docker' not in sys.modules, "Docker not available") 
    def test_init_ubuntu_docker(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        self.assertIn('ubuntu', controller.image_os)
        self.assertIn('latest', controller.image_tag)

 #   @unittest.skipIf('docker' not in sys.modules, "Docker not available") 
 #   def test_create_ubuntu_docker_spack(self):
 #       controller = DockerController()
 #       controller.init_image('ubuntu')
 #       controller.install_spack()
 #       controller.execute_build("unittesting")
