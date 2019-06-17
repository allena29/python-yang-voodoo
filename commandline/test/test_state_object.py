import prompt_toolkit
import unittest
from yangvoodoo.VoodooNode import Voodoo
from mock import Mock
from cli import cli, state, MyValidator


class test_validation_and_completion(unittest.TestCase):
    def setUp(self):
        self.log = Mock()
        self.state_object = state(self.log)
        self.state_object.buffer = Mock()

    def test_get_completions(self):
        # Build
        document_text = "set simple"
        parts = ["set", "simple"]

        subject = self.state_object
        subject.current_node = Voodoo()
        subject.current_node._children = Mock(return_value=['simpleleaf', 'simplelist'])

        # Act
        result = list(subject.get_completions(document_text, parts))

        # Assert
        self.assertEqual(result, [('leaf', 'simpleleaf', True), ('list', 'simplelist', True)])

    def test_position(self):
        # Build
        document_text = "set simp"

        subject = self.state_object
        subject.last_character_position = 6

        # Action
        subject.update_position_and_current_command(document_text)

        # Assert
        self.assertEqual(subject.direction, 'forwards')

    def test_position_backwards(self):
        # Build
        document_text = "set simp"

        subject = self.state_object
        subject.last_character_position = 9

        # Action
        subject.update_position_and_current_command(document_text)

        # Assert
        self.assertEqual(subject.direction, 'backwards')

    def test_position_update_nodes(self):
        """
        This stest makes sure what when we press space after
        """
        # Build
        document_text = "set bronze "
        child_node_to_replace_current_node_with = Mock()

        subject = self.state_object
        subject.go_to_next_node_at_position = 10
        subject.next_node_name = 'bronze'
        subject.current_node = {'bronze': child_node_to_replace_current_node_with}

        # Act
        subject.update_position_and_current_command(document_text)
        subject.update_current_node(document_text)

        # Assert
        self.assertEqual(subject.go_to_next_node_at_position, 0)
        self.assertEqual(subject.current_node,  child_node_to_replace_current_node_with)
        self.assertEqual(subject.go_to_parent_node_at_position, [0, 11])
