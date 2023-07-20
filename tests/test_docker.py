import sys
import unittest
from e4s_alc import E4S_ALC_HOME
from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
from e4s_alc.model.container.docker import DockerController
from e4s_alc.model.container.podman import PodmanController
from e4s_alc.model.container.singularity import SingularityController
from e4s_alc.model.init import InitModel
import types
from subprocess import Popen, PIPE

from e4s_alc import logger

import docker

logger.set_log_level("FATAL")

class DockerTests(unittest.TestCase):
    def setUp(self):
        initCommand = InitModel()
        args = types.SimpleNamespace() 
        args.backend="docker"
        args.parent=None
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
    def test_create_ubuntu_docker_spack(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        controller.add_spack_package_commands(['zlib'])
        self.assertIsNone(controller.execute_build("unittesting"))
        p = Popen(["docker", "run", "--env", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/spack/bin", "unittesting", "spack", "find"], stdout=PIPE)
        stdout, _ = p.communicate()
        self.assertIn(b'zlib@', stdout)
        controller.delete_image(['ubuntu', 'unittesting'], True)

    @unittest.skipIf('docker' not in sys.modules, "Docker not available")
    def test_create_ubuntu_docker_spack_yaml(self):
        controller = DockerController()
        controller.init_image('ubuntu')
        controller.add_ubuntu_package_commands('')
        controller.install_spack()
        spack_yamls_dir = E4S_ALC_HOME + '/tests/assets/spack_yamls'
        controller.spack_yaml_configuration("test_spack.yaml", spack_yamls_dir=spack_yamls_dir)
        self.assertIsNone(controller.execute_build("unittesting"))
        p = Popen(["docker", "run", "--env", "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/spack/bin", "unittesting", "spack", "find"], stdout=PIPE)
        stdout, _ = p.communicate()
        self.assertIn(b'zlib@', stdout)
        self.assertIn(b'tcl@', stdout)
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
