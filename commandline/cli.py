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
# from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory


class MyCompleter(Completer):
    def get_completions(self, document, complete_event, _state_object_and_log=None):
        global log, state_object
        if _state_object_and_log:
            (state_object, log) = _state_object_and_log

        complete_this = document.text
        if not state_object.current_command:
            options = state_object.get_command_completions(complete_this, validator=False)
        else:
            parts = state._get_space_separated_values(document.text)
            # This is required to make sure the completions for the next node work - otherwise
            # it tries to match the previous word
            if document.text[-1] == ' ':
                parts.pop()
                parts.append('')
            options = state_object.get_completions(complete_this, parts, validator=False)

        for (option, display, visibility) in options:
            if visibility:
                yield Completion(
                    option, start_position=0,
                    display=HTML('<b>%s</b> ' % (display))
                )


class MyValidator(Validator):

    def _error(self, message, delete_last_character=True, terminal_bell=True):
        global log
        if terminal_bell:
            sys.stdout.write("\a")
        if delete_last_character:
            if state_object.direction == 'backwards':
                log.info('going backwards so ignoring backwspace')
                return
            state_object.buffer.delete_before_cursor(1)
        raise ValidationError(message=message, cursor_position=0)

    def validate(self, document, _state_object_and_log=None):
        global state_object, log
        if _state_object_and_log:
            (state_object, log) = _state_object_and_log

        if len(document.text) > 1:
            if document.text[-2:] == '  ':
                self._error("stop pressing the space bar", True, True)

        if state_object.stop_completions_and_validation:
            return

        parts = state._get_space_separated_values(document.text)
        if len(parts) == 0:
            return True

        state_object.update_position_and_current_command(document.text)

        if not state_object.current_command:
            options = state_object.get_command_completions(document.text)
        else:
            options = state_object.get_completions(document.text, parts)

        num_options = 0
        for incomplete_part, completion, visibility in options:
            if visibility:
                num_options = num_options + 1

        if num_options == 1:
            state_object.update_current_node(document.text)
            return True

        if state_object.number_of_trailing_parts > 0:
            if len(parts) > state_object.last_part_count + state_object.number_of_trailing_parts:
                self._error("Too many values")
            if len(parts) == state_object.last_part_count + state_object.number_of_trailing_parts and document.text[-1] == ' ':
                self._error("No more!")
        elif num_options > 1:
            self._error("Not enough!", delete_last_character=False, terminal_bell=False)
        elif not document.text[-1] == ' ' and state_object.number_of_trailing_parts == 0:
            self._error("Invalid input")


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

    def __init__(self, log=None):
        self.log = log
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
        self.go_to_next_node_at_position = 0
        self.go_to_parent_node_at_position = [0]
        self.parent_node = [self.root]
        self.number_of_trailing_parts = 0
        self.next_node_number_of_trailing_parts = 0
        self.direction = "never moved"
        self.next_node_name = ""

    def update_position_and_current_command(self, document_text):
        # self.log.info("Consisdering %s-command  for __%s__ (last %s, number of trailing %s, goto-next-node %s)", self.mode, document_text,
        #               self.last_character_position, self.next_node_number_of_trailing_parts, self.go_to_next_node_at_position)
        # self.log.info("Node %s", self.current_node)
        if len(document_text) < self.last_character_position:
            self.direction = 'backwards'
        else:
            self.direction = 'forwards'

        if self.direction == 'backwards' and len(document_text) == self.reset_current_command:
            self.current_command = None
            self.reset_current_command = 0

        self.log.info('%s/%s go-parent%s go-next%s', self.direction, len(document_text),
                      self.go_to_parent_node_at_position, self.go_to_next_node_at_position)

        if self.direction == 'backwards':
            self.log.info('going backwards...........%s', len(document_text))
            if len(document_text) <= self.go_to_parent_node_at_position[-1]:
                parent_node_pos = self.go_to_parent_node_at_position.pop()
                parent_node = self.parent_node.pop()
                self.log.info(' set current node with a switcher-roo to %s', parent_node)
                self.log.info(' %s ..%s ', len(document_text), document_text)
                self.current_node = parent_node
                self.log.info(' parentNode_pos %s', parent_node_pos)
        self.last_character_position = len(document_text)

    def update_current_node(self, document_text):
        """
        This only gets called when we have exactly 1 completion
        """
        if self.direction == 'forwards' and len(document_text) >= self.go_to_next_node_at_position and self.go_to_next_node_at_position > 0:
            self.parent_node.append(self.current_node)
            self.go_to_parent_node_at_position.append(len(document_text))
            self.current_node = self.current_node[self.next_node_name]
            self.number_of_trailing_parts = self.next_node_number_of_trailing_parts
            self.go_to_next_node_at_position = 0

            self.log.info('SWITCHING FORWARD %s/%s go-parent%s go-next%s ', self.direction, len(document_text),
                          self.go_to_parent_node_at_position, self.go_to_next_node_at_position)

    def get_command_completions(self, document_text, validator=True):
        """
        we track which command is current, and based on direction will reset it to None
        """
        log.info('GCC: %s %s __%s__', self.direction, self.current_command, document_text)
        completions = self.OPER_COMMANDS
        if self.mode == 1:
            completions = self.CONF_COMMANDS

        for (completion, visibility) in completions:
            if completion[0:len(document_text)] == document_text:
                if not (visibility == 0 and not validator):
                    if validator and document_text == completion:
                        self.current_command = completion
                    yield (completion[len(document_text):], completion, visibility)

    def get_completions(self, document_text, parts, validator=True):
        if self.number_of_trailing_parts > 0:
            return

        last_part = parts[-1]
        self.log.info('GC : len(%s)%s/%s doctext:%s_ lastpart:%s_ ', len(document_text), self.direction,
                      self.current_command, document_text, last_part)
        self.log.info('   : %s/%s', self.current_node, self.parent_node)

        if isinstance(self.current_node, yangvoodoo.VoodooNode.Voodoo):
            # self.log.info("getting completsions from %s", self.current_node)
            completions = self.current_node._children()
            # self.log.info("%s" % (str(completions)))
        else:
            # self.log.info("skipping completions becuase node doesnt look voodoo like %s", self.current_node)
            return True

        answers = []
        for completion in completions:
            if completion[0:len(last_part)] == last_part:
                answers.append((completion[len(last_part):], completion, True))

        if len(answers) == 1:
            # self.go_to_parent_node_at_position = len(document_text)
            # self.parent_node = self.current_node
            # self.parent_node_name = self.next_node_name
            self.next_node_name = answers[0][1]

            self.next_node_number_of_trailing_parts = state.how_many_trailing_parts(self.current_node, answers[0][1])
            # self.number_of_trailing_parts = state.how_many_trailing_parts(self.current_node, answers[0][1])
            self.go_to_next_node_at_position = len(document_text) - len(last_part) + len(answers[0][1])
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
        self.go_to_parent_node_at_position = [0]
        self.parent_node = []
        self.go_to_next_node_at_position = 0
        self.next_node_name = ""
        self.last_part_count = 0
        self.next_node_number_of_trailing_parts = 0

    def reset_oper(self):
        self.mode = 0
        self.current_command = None
        self.number_of_trailing_parts = 0
        self.go_to_parent_node_at_position = [0]
        self.parent_node = []
        self.go_to_next_node_at_position = 0
        self.next_node_name = ""
        self.last_part_count = 0
        self.next_node_number_of_trailing_parts = 0

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
                                  # auto_suggest=AutoSuggestFromHistory()
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
    state_object = state(log)
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
