import sys
import unittest
from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
from e4s_alc.controller.backend.singularity import SingularityBackend, SINGULARITY_IMAGES
import types
from subprocess import Popen, PIPE

import logging
logger = logging.getLogger('core')

class SingularityTests(unittest.TestCase):
#    def setUp(self):
#
#
#    def test_create_empty_image_singularity(self):
#
#    def test_init_ubuntu_singularity(self):
#
#    def test_create_ubuntu_singularity(self):
#    
#    def test_create_ubuntu_singularity_podman(self):
#
#    def test_create_ubuntu_singularity_spack(self):
#
#    def test_create_ubuntu_singularity_spack_yaml(self):
#
#    def test_find_image(self):
#
#    def test_pull_image(self):
#
#    def test_delete_image(self):
#
#    def test_parse_os_release(self):
#
#    def test_parse_environment(self):
