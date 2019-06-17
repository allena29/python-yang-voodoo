#!/usr/bin/env python3
import yangvoodoo
from logsink import LogWrap
import re
import sys
import time
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory


class MyCompleter(Completer):
    def get_completions(self, document, complete_event):
        global log, state_object

        if not state_object.current_command:
            options = state_object.get_command_completions(document, validator=False)
        else:
            parts = state._get_space_separated_values(document.text)
            options = state_object.get_completions(document, parts, validator=False)

        for (option, display) in options:
            yield Completion(
                option, start_position=0,
                display=HTML('<b>%s</b> ' % (display))
            )


class MyValidator(Validator):
    def validate(self, document):
        global log, state_object
        if state_object.stop_completions_and_validation:
            return
        parts = state._get_space_separated_values(document.text)
        if len(parts) == 0:
            return True

        state_object.update_position_and_current_command(document)

        if not state_object.current_command:
            options = state_object.get_command_completions(document)
        else:
            options = state_object.get_completions(document, parts)

        num_options = 0
        for option in options:
            num_options = num_options + 1

        if num_options == 1:
            return True

        log.info("__%s__ trailing_parts %s options %s", document.text, state_object.number_of_trailing_parts, num_options)
        if state_object.number_of_trailing_parts > 0:
            if len(parts) > state_object.last_part_count + state_object.number_of_trailing_parts:
                state_object.buffer.delete_before_cursor(1)
                raise ValidationError(message="Too many keys/leaves", cursor_position=0)
            if len(parts) == state_object.last_part_count + state_object.number_of_trailing_parts and document.text[-1] == ' ':
                state_object.buffer.delete_before_cursor(1)
                raise ValidationError(message="No more!", cursor_position=0)
        elif num_options > 1:
            raise ValidationError(message="Not enough!", cursor_position=0)

        elif not document.text[-1] == ' ' and state_object.number_of_trailing_parts == 0:
            sys.stdout.write("\a")
            state_object.buffer.delete_before_cursor(1)
            raise ValidationError(message='Invalid input', cursor_position=0)


class formats:
    @staticmethod
    def bottom_toolbar():
        return HTML('Yang Voodoo Cli')

    @staticmethod
    def exit_conf_mode():
        print("[ok][%s]" % (formats.get_time()))

    @staticmethod
    def enter_conf_mode():
        print("[ok][%s]" % (formats.get_time()))

    @staticmethod
    def get_time():
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())


class state:

    OPER_COMMANDS = [('conf', 0),  ('configure', 1), ('config', 0), ('show configuration ', 1), ('show config ', 0), ('exit', 1)]
    CONF_COMMANDS = [('set ', 1), ('delete ', 1), ('exit', 1), ('validate', 1), ('commit', 1), ('show ', 1), ('show', 0)]
    # allow '', "" quote strings or non space containg strings.
    REGEX_SPACE_SEPARATOR = re.compile(r"'([^']+)'|\"([^\"]+)\"|(\S+)")

    """
    The state object tracks what the user is typing, every keystroke fires a validator, and completer.

    The validator fires first, and raises an exception if the input does not look valid. In that case we
    don't need to worry about the completer firing.

    """

    def __init__(self):
        self.mode = 0
        self.first_command = None
        self.session = yangvoodoo.DataAccess()
        self.session.connect("integrationtest", yang_location="../yang")
        self.root = self.session.get_node()
        self.current_node = self.root
        self.last_character_position = 0
        self.current_command = None
        self.stop_completions_and_validation = False
        self.reset_current_command = 0
        self.number_of_trailing_parts = 0

    def update_position_and_current_command(self, document):
        log.info("Consisdering %s-command  for __%s__", self.mode, document.text)

        if len(document.text) < self.last_character_position:
            self.direction = 'backwards'
        else:
            self.direction = 'forwards'

        if self.direction == 'backwards' and len(document.text) == self.reset_current_command:
            self.current_command = None
            self.reset_current_command = 0

        if self.direction == 'forwards' and len(document.text) >= self.go_to_next_node_at_position and self.go_to_next_node_at_position > 0:
            self.current_node = self.current_node[self.next_node_name]
            self.go_to_next_node_at_position = 0
        self.last_character_position = len(document.text)

    def get_command_completions(self, document, validator=True):
        """
        we track which command is current, and based on direction will reset it to None
        """
        log.info('GCC: %s %s __%s__', self.direction, self.current_command, document.text)
        completions = self.OPER_COMMANDS
        if self.mode == 1:
            completions = self.CONF_COMMANDS

        for (completion, visibility) in completions:
            if completion[0:len(document.text)] == document.text:
                if not (visibility == 0 and not validator):
                    if validator and document.text == completion:
                        self.current_command = completion

                    yield (completion[len(document.text):], completion)

    def get_completions(self, document, parts, validator=True):
        """
        """
        if self.number_of_trailing_parts > 0:
            log.info("No offeringup any completions")
            return

        last_part = parts[-1]
        log.info('GC : len(%s) %s %s __%s__  __%s__', len(document.text), self.direction, self.current_command, document.text, last_part)
        completions = self.current_node._children()

        answers = []
        for completion in completions:
            if completion[0:len(last_part)] == last_part:
                answers.append((completion[len(last_part):], completion))

        if len(answers) == 1:
            log.info("only one option left")

            self.go_to_parent_node_at_position = len(document.text)
            self.parent_node = self.current_node
            self.previous_node_name = self.next_node_name
            self.next_node_name = answers[0][1]
            self.number_of_trailing_parts = state.how_many_trailing_parts(self.current_node, answers[0][1])
            self.go_to_next_node_at_position = len(document.text) - len(last_part) + len(answers[0][1]) + 1
            self.last_part_count = len(parts)

        for answer in answers:
            yield answer

    @staticmethod
    def how_many_trailing_parts(current_node, last_part):
        """
        Determine how many trailing parts are required.

        A leaf of empty type has 0 trailing parts
        A leaf has exactly 1 trailing part
        A list may have as many trailing parts as there are keys.
        """
        node = current_node[last_part]

        if isinstance(node, yangvoodoo.VoodooNode.Node):
            node_type = node._NODE_TYPE
        else:
            return 1

        return 0

    def reset_conf(self):
        self.mode = 1
        self.current_command = None
        self.number_of_trailing_parts = 0
        self.go_to_parent_node_at_position = 0
        self.go_to_next_node_at_position = 0
        self.next_node_name = ""
        self.previous_node_name = ""
        self.last_part_count = 0

    def reset_oper(self):
        self.mode = 0
        self.current_command = None
        self.number_of_trailing_parts = 0
        self.go_to_parent_node_at_position = 0
        self.go_to_next_node_at_position = 0
        self.next_node_name = ""
        self.previous_node_name = ""
        self.last_part_count = 0

    @staticmethod
    def _get_space_separated_values(input):
        """
        Get space separated values, ignoring quoted stirngs.
        """
        answer = []
        for match1, match2, match3 in state.REGEX_SPACE_SEPARATOR.findall(input):
            if match3 != '':
                answer.append(match3)
            elif match2 != '':
                answer.append(match2)
            else:
                answer.append(match1)
        return answer


class cli:

    # allow \ escpaed scpaes,
    # REGEX_SPACE_SEPARATOR = re.compile(r"(\S+\\ \S+)|((')([^']+)('))|((\")[^\"]+(\"))|(\S+)")
    # REGEX_SPACE_SEPARATOR = re.compile(r"('([^']+)')|(\"([^\"])+\")|(\S+)")

    def __init__(self, state_object):
        self.log = LogWrap("cli")
        self.log.info("CLI Started")
        self.user = "steg"
        self.host = "localhost"
        self.exit = False

        self.state_object = state_object

        self.prompt = self._get_prompt_session()
        self.state_object.buffer = self.prompt.default_buffer

    def _get_prompt_session(self):
        our_history = FileHistory('.yangvoodoo-cli-history')

        return PromptSession(history=our_history)

    def _get_completer(self):
        return WordCompleter(['set ', 'show '])

    def _prompt_and_wait_for_cli(self):
        if self.state_object.mode == 1:
            our_prompt = "\n[edit]\n%s@%s%% " % (self.user, self.host)
        else:
            our_prompt = "%s@%s> " % (self.user, self.host)

        return self.prompt.prompt(our_prompt,
                                  bottom_toolbar=formats.bottom_toolbar,
                                  completer=MyCompleter(),
                                  validator=MyValidator(),
                                  complete_while_typing=True,
                                  validate_while_typing=True,
                                  vi_mode=True,
                                  auto_suggest=AutoSuggestFromHistory()
                                  )

    def loop(self):
        try:
            print('Welcome goes here')
            while not self.exit:
                try:
                    cmd = self._prompt_and_wait_for_cli()
                    if self.state_object.mode == 0:
                        self._process_oper_command(cmd)
                    else:
                        self._process_conf_command(cmd)
                except KeyboardInterrupt:
                    pass
                except EOFError:
                    if self.state_object.mode == 1:
                        self.state_object.reset_oper()
                        print("\n[ok][%s]" % (formats.get_time()))
                        self.state_object.reset_oper()
                        continue
                    break
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass

    def _process_oper_command(self, cmd):
        if cmd == "exit":
            print("Goodbye!")
            sys.exit(0)

        if cmd == "conf" or cmd == "configure" or cmd == "config":
            print("Entering configuration mode")
            print("[ok][%s]" % (formats.get_time()))
            self.state_object.reset_conf()
            return True

    def _process_conf_command(self, cmd):
        self.log.info('processing conf _%s_', cmd)
        if cmd == "exit":
            print("\n[ok][%s]" % (formats.get_time()))
            self.state_object.reset_oper()
            return True
        else:
            self.log.info('operate on voodoo node: %s', self.state_object.current_node)
            # here we don't have the correct voodoo node out of the box
            # in the example 'set cli a apple <X>' we get the voodoo node a
            parts = state._get_space_separated_values(cmd)


if __name__ == '__main__':
    log = LogWrap("cli-customer-completer")
    state_object = state()
    c = cli(state_object)
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as file_handle:
            line = file_handle.readline()
            while line != "":
                if line[0] == "O":
                    c._process_oper_command(line[2:].rstrip())
                if line[0] == "I":
                    c._process_conf_command(line[2:].rstrip())
                line = file_handle.readline()

    c.loop()
#
