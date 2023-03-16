import sys
import unittest
from unittest.mock import patch
from e4s_alc.cli.__main__ import COMMAND as cli_main_cmd
import e4s_alc

class CreateTests(unittest.TestCase):
    def test_create_empty_image(self):
        with self.assertRaises(SystemExit) as system_exit:
            cli_main_cmd.main(['create'])
