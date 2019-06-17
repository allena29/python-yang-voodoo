import prompt_toolkit
import unittest
from mock import Mock
from cli import cli, state, MyValidator


class test_validation_and_completion(unittest.TestCase):
    def setUp(self):
        self.log = Mock()
        self.state_object = state(self.log)
        self.state_object.buffer = Mock()

    def test_validation_error_raised_when_holding_down_space(self):
        # Build
        self.state_object.current_command = 'set'
        self.state_object.direction = 'forwards'
        self.state_object.stop_completions_and_validation = False
        self.state_object.number_of_trailing_parts = 1
        self.state_object.last_part_count = 6
        self.state_object.get_completions = Mock(return_value=[])

        document = Mock()
        document.text = "set bronze silver gold platinum  "
        self.subject = MyValidator()

        # Act
        with self.assertRaises(prompt_toolkit.validation.ValidationError) as context:
            result = self.subject.validate(document, (self.state_object, self.log))
        self.assertEqual(str(context.exception), "stop pressing the space bar")
        self.state_object.buffer.delete_before_cursor.assert_called_once_with(1)

    def test_validation_error_raised_when_not_quoting_a_leaf_stirng(self):
        # Build
        self.state_object.current_command = 'set'
        self.state_object.direction = 'forwards'
        self.state_object.stop_completions_and_validation = False
        self.state_object.number_of_trailing_parts = 1
        self.state_object.last_part_count = 6
        self.state_object.get_completions = Mock(return_value=[])

        document = Mock()
        document.text = "set bronze silver gold platinum deep sdsdfhdsfhsdf fsdf"
        self.subject = MyValidator()

        # Act
        with self.assertRaises(prompt_toolkit.validation.ValidationError) as context:
            result = self.subject.validate(document, (self.state_object, self.log))
        self.assertEqual(str(context.exception), "Too many values")
        self.state_object.buffer.delete_before_cursor.assert_called_once_with(1)

    def test_validate_of_set_string(self):
        # Build
        self.state_object.current_command = 'set'
        self.state_object.direction = 'forwards'
        self.state_object.stop_completions_and_validation = False
        self.state_object.number_of_trailing_parts = 1
        self.state_object.last_part_count = 6
        self.state_object.get_completions = Mock(return_value=[])

        document = Mock()
        document.text = "set bronze silver gold platinum deep sdsf"
        self.subject = MyValidator()

        # Act
        result = self.subject.validate(document, (self.state_object, self.log))

        # Assert
        # No exception raised

    def test_validation_error_raised_when_not_unique_enough(self):
        """
        Note this error doesn't actually delete the output.
        """
        # Build
        self.state_object.current_command = 'set'
        self.state_object.direction = 'forwards'
        self.state_object.stop_completions_and_validation = False
        self.state_object.number_of_trailing_parts = 0
        self.state_object.last_part_count = 2
        self.state_object.get_completions = Mock(return_value=[
            ('leaf', 'simpleleaf', True), ('list', 'simplelist', True)
        ])

        document = Mock()
        document.text = "set simple"
        self.subject = MyValidator()

        # Act
        with self.assertRaises(prompt_toolkit.validation.ValidationError) as context:
            result = self.subject.validate(document, (self.state_object, self.log))
        self.assertEqual(str(context.exception), "Not enough!")

        self.state_object.buffer.delete_before_cursor.assert_not_called()
