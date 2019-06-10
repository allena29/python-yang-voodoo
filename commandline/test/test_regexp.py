import unittest
import re
from cli import cli, state


class test_cli(unittest.TestCase):

    def setUp(self):
        self.state = state()
        self.subject = cli(self.state)

    def test_space_separator(self):
        result = self.state._get_space_separated_values("no")
        self.assertEqual(result, ["no"])

        result = self.state._get_space_separated_values("'single quote' not single quote")
        self.assertEqual(result, ["single quote", "not", "single", "quote"])

        result = self.state._get_space_separated_values('"double quote" not double quote')
        self.assertEqual(result, ["double quote", "not", "double", "quote"])
