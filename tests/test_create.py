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

class DockerTests(unittest.TestCase):
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
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_create_ubuntu_docker_spack(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_find_image(self):
        controller = DockerController()
        controller_2 = DockerController()
        controller.pull_image('ubuntu')
        controller_2.find_image("ubuntu")
        self.assertEqual(controller_2.image, "ubuntu")
        controller.delete_image(['ubuntu'], True)
        with self.assertRaises(SystemExit) as system_exit:
            controller_2.find_image("ubuntuifkajsh")

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_pull_image(self):
        controller = DockerController()
        self.assertIsNone(controller.pull_image('ubuntu'))
        controller.delete_image(['ubuntu'], True)
        with self.assertRaises(SystemExit) as system_exit:
            controller.pull_image('ubuntuikljafhsdlkfjs')

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_delete_image(self):
        controller = DockerController()
        controller.pull_image('ubuntu')
        with self.assertRaises(SystemExit) as system_exit:
            controller.delete_image(['ubuntufklashdjfkl'], True)
        self.assertIsNone(controller.delete_image(['ubuntu'], True))

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_parse_os_release(self):
        controller = DockerController()
        controller.pull_image('ubuntu:18.04')
        controller.parse_os_release()
        self.assertEqual(controller.os_release['PRETTY_NAME'], 'Ubuntu 18.04.6 LTS')
        controller.delete_image(['ubuntu:18.04'], True)

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_parse_environment(self):
        controller = DockerController()
        controller.pull_image('ubuntu:18.04')
        controller.parse_environment()
        self.assertEqual(controller.environment['PATH'], '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
        controller.delete_image(['ubuntu:18.04'], True)

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
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_create_ubuntu_podman_spack(self):
        controller = PodmanController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_find_image(self):
        controller = PodmanController()
        controller_2 = PodmanController()
        controller.pull_image('ubuntu')
        controller_2.find_image("ubuntu")
        self.assertEqual(controller_2.image, "ubuntu")
        controller.delete_image(['ubuntu'], True)
        with self.assertRaises(SystemExit) as system_exit:
            controller_2.find_image("ubuntuifkajsh")

    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_pull_image(self):
        controller = PodmanController()
        self.assertIsNone(controller.pull_image('ubuntu'))
        controller.delete_image(['ubuntu'], True)
        with self.assertRaises(SystemExit) as system_exit:
            controller.pull_image('ubuntuikljafhsdlkfjs')

    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_delete_image(self):
        controller = PodmanController()
        controller.pull_image('ubuntu')
        with self.assertRaises(SystemExit) as system_exit:
            controller.delete_image(['ubuntufklashdjfkl'], True)
        self.assertIsNone(controller.delete_image(['ubuntu'], True))

    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_parse_os_release(self):
        controller = PodmanController()
        controller.pull_image('ubuntu:18.04')
        controller.parse_os_release()
        self.assertEqual(controller.os_release['PRETTY_NAME'], 'Ubuntu 18.04.6 LTS')
        controller.delete_image(['ubuntu:18.04'], True)

    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_parse_environment(self):
        controller = PodmanController()
        controller.pull_image('ubuntu:18.04')
        controller.parse_environment()
        self.assertEqual(controller.environment['PATH'], '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
        controller.delete_image(['ubuntu:18.04'], True)

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
        controller.parent.delete_image(controller, ['ubuntu'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_create_ubuntu_singularity(self):
        controller = SingularityController()
        controller.init_image('ubuntu')
        controller.parent = DockerController
        controller.client = controller.client_docker
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['unittesting.sif'], True)
        controller.parent.delete_image(controller, ['unittesting'], True)
        controller.parent.delete_image(controller, ['ubuntu'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    @unittest.skipIf('podman' not in sys.modules, "Podman not available")
    def test_create_ubuntu_singularity_podman(self):
        controller = SingularityController()
        controller.init_image('ubuntu')
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['unittesting.sif'], True)
        controller.parent.delete_image(controller, ['unittesting'], True)
        controller.parent.delete_image(controller, ['ubuntu'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_create_ubuntu_singularity_spack(self):
        controller = SingularityController()
        controller.init_image('ubuntu')
        controller.parent = DockerController
        controller.client = controller.client_docker
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        self.assertIsNone(controller.execute_build("unittesting"))
        controller.delete_image(['unittesting.sif'], True)
        controller.parent.delete_image(controller, ['unittesting'], True)
        controller.parent.delete_image(controller, ['ubuntu'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    def test_find_image(self):
        controller = SingularityController()
        controller_2 = SingularityController()
        controller.pull_image('ubuntu')
        controller_2.find_image("ubuntu")
        self.assertEqual(controller_2.image, "ubuntu")
        controller.parent.delete_image(controller, ['ubuntu'], True)
        with self.assertRaises(SystemExit) as system_exit:
            controller_2.find_image("ubuntuifkajsh")

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    def test_pull_image(self):
        controller = SingularityController()
        self.assertIsNone(controller.pull_image('ubuntu'))
        controller.parent.delete_image(controller, ['ubuntu'], True)
        with self.assertRaises(SystemExit) as system_exit:
            controller.parent.delete_image(controller, ['ubuntudsg'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    def test_delete_image(self):
        controller = SingularityController()
        controller.pull_image('ubuntu')
        with self.assertRaises(SystemExit) as system_exit:
            controller.parent.delete_image(controller, ['ubuntudsg'], True)
        self.assertIsNone(controller.parent.delete_image(controller, ['ubuntu'], True))

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    def test_parse_os_release(self):
        controller = SingularityController()
        controller.pull_image('ubuntu:18.04')
        controller.parse_os_release()
        self.assertEqual(controller.os_release['PRETTY_NAME'], 'Ubuntu 18.04.6 LTS')
        controller.parent.delete_image(controller, ['ubuntu:18.04'], True)

    @unittest.skipIf('spython' not in sys.modules, "Singularity not available")
    def test_parse_environment(self):
        controller = SingularityController()
        controller.pull_image('ubuntu:18.04')
        controller.parse_environment()
        self.assertEqual(controller.environment['PATH'], '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin')
        controller.parent.delete_image(controller, ['ubuntu:18.04'], True)
