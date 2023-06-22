import unittest
from e4s_alc.mvc.controller import Controller
from e4s_alc import logger

logger.set_log_level("FATAL")

ASSETS_DIRECTORY = "./tests/assets/"

class ControllerTests(unittest.TestCase):

    def test_read_args_file(self):
        controller = Controller("test")
        data = controller.read_args_file(ASSETS_DIRECTORY + "testconfig.json")
        self.assertEqual(data['image'], 'ubuntu:22.04')
        self.assertEqual(data['name'], 'test-configuration-file')
        self.assertEqual(data['spack'], True)
        self.assertEqual(data['spack-packages'], ['kokkos', 'raja'])
        self.assertEqual(data['os-packages'], ['neovim', 'valgrind'])
        
