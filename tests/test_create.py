import sys
import unittest
from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
from e4s_alc.model.container.docker import DockerController
from e4s_alc.model.container.podman import PodmanController
from e4s_alc.model.container.singularity import SingularityController
from e4s_alc.model.init import InitModel
import types
from e4s_alc import logger

import docker
import podman
import spython

logger.set_log_level("FATAL")

class DockerCreateTests(unittest.TestCase):
    def setUp(self):
        initCommand = InitModel()
        args = types.SimpleNamespace() 
        args.backend="docker"
        initCommand.main(args)

    def test_create_empty_image_docker(self):
        with self.assertRaises(SystemExit) as system_exit:
            cli_main_cmd.main(['create'])

    @unittest.skipIf('docker' not in sys.modules, "Docker not available") 
    def test_init_ubuntu_docker(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        self.assertIn('ubuntu', controller.image_os)
        self.assertIn('latest', controller.image_tag)
        controller.delete_image(['ubuntu'], True)

    @unittest.skipIf('docker' not in sys.modules, "Docker not available") 
    def test_create_ubuntu_docker(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        controller.execute_build("unittesting")
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('docker' not in sys.modules, "Docker not available") 
    def test_create_ubuntu_docker_spack(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['ubuntu', 'unittesting'], True)

class PodmanCreateTests(unittest.TestCase):
    def setUp(self):
        initCommand = InitModel()
        args = types.SimpleNamespace() 
        args.backend="podman"
        initCommand.main(args)

    def test_create_empty_image_podman(self):
        with self.assertRaises(SystemExit) as system_exit:
            cli_main_cmd.main(['create'])

    @unittest.skipIf('podman' not in sys.modules, "Podman not available") 
    def test_init_ubuntu_podman(self):
        controller = PodmanController()
        controller.init_image('ubuntu')
        self.assertIn('ubuntu', controller.image_os)
        self.assertIn('latest', controller.image_tag)
        controller.delete_image(['ubuntu'], True)

    @unittest.skipIf('podman' not in sys.modules, "Podman not available") 
    def test_create_ubuntu_podman(self):
        controller = PodmanController()
        controller.init_image('ubuntu')
        controller.execute_build("unittesting")
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('podman' not in sys.modules, "Podman not available") 
    def test_create_ubuntu_podman_spack(self):
        controller = PodmanController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['ubuntu', 'unittesting'], True)

class SingularityCreateTests(unittest.TestCase):
    def setUp(self):
        initCommand = InitModel()
        args = types.SimpleNamespace() 
        args.backend="singularity"
        initCommand.main(args)

    def test_create_empty_image_singularity(self):
        with self.assertRaises(SystemExit) as system_exit:
            cli_main_cmd.main(['create'])

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available") 
    def test_init_ubuntu_singularity(self):
        controller = SingularityController()
        controller.init_image('ubuntu')
        self.assertIn('ubuntu', controller.image_os)
        self.assertIn('latest', controller.image_tag)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available") 
    def test_create_ubuntu_singularity(self):
        controller = SingularityController()
        controller.init_image('ubuntu')
        controller.execute_build("unittesting")
        controller.delete_image(['unittesting.sif'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available") 
    def test_create_ubuntu_singularity_spack(self):
        controller = SingularityController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['unittesting.sif'], True)
