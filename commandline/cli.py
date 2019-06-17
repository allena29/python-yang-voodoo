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
    def get_completions(self, document, complete_event, _state_object_and_log=None):
        global log, state_object
        if _state_object_and_log:
            (state_object, log) = _state_object_and_log
        #
        # complete_this = document.text
        # if not state_object.current_command:
        #     options = state_object.get_command_completions(complete_this, validator=False)
        # else:
        #     parts = state._get_space_separated_values(document.text)
        #     # This is required to make sure the completions for the next node work - otherwise
        #     # it tries to match the previous word
        #     if document.text[-1] == ' ':
        #         parts.pop()
        #         parts.append('')
        #     options = state_object.get_completions(complete_this, parts, validator=False)
        #
        # for (option, display, visibility) in options:
        #     if visibility:

        display = 'dummy'
        option = 'dummy'
        yield Completion(
            option, start_position=0,
            display=HTML('<b>%s</b> ' % (display))
        )


class MyValidator(Validator):

    def _error(self, message, delete_last_character=True, terminal_bell=True):
        if state_object.direction == 'backwards':
            log.info('going backwards so ignoring backwspace')
            return
        if terminal_bell:
            sys.stdout.write("\a")
        if delete_last_character:
            state_object.buffer.delete_before_cursor(1)
        raise ValidationError(message=message, cursor_position=0)

    def validate(self, document, _state_object_and_log=None):
        global state_object, log
        if _state_object_and_log:
            (state_object, log) = _state_object_and_log

        if len(document.text) > 1:
            if document.text[-2:] == '  ':
                self._error("stop pressing the space bar", True, True)

        # if state_object.stop_completions_and_validation:
        #     return
        #
        # parts = state._get_space_separated_values(document.text)
        # if len(parts) == 0:
        #     return True
        #
        # state_object.update_position_and_current_command(document.text)
        #
        # if not state_object.current_command:
        #     options = state_object.get_command_completions(document.text)
        # else:
        #     options = state_object.get_completions(document.text, parts)
        #
        # num_options = 0
        # matching_an_option = False
        # for incomplete_part, completion, visibility in options:
        #     if completion == parts[-1]:
        #         matching_an_option = True
        #     if visibility:
        #         num_options = num_options + 1
        #
        # if num_options == 1:
        #     state_object.update_current_node(document.text)
        #     return True
        #
        # if state_object.number_of_trailing_parts > 0:
        #     if len(parts) > state_object.last_part_count + state_object.number_of_trailing_parts:
        #         self._error("Too many values")
        #     if len(parts) == state_object.last_part_count + state_object.number_of_trailing_parts and document.text[-1] == ' ':
        #         self._error("No more!")
        # elif num_options > 1:
        #     if matching_an_option:
        #         return True
        #     # This logic isn't just on the number of options
        #     # Consider the case of cli/aaaa
        #     # and cli/a
        #     # When document.text = a we have enough options
        #
        #     self._error("Not enough!", delete_last_character=False, terminal_bell=False)
        # elif not document.text[-1] == ' ' and state_object.number_of_trailing_parts == 0:
        #     self._error("Invalid input")
        #


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

    def reset_conf(self):
        self.mode = 1

    def reset_oper(self):
        self.mode = 0

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

            print(parts)
            print(self.state_object.next_node_number_of_trailing_parts)

            self.state_object.reset_conf()


if __name__ == '__main__':
    print("""


          We should use shelx to unescape strings.
          
 shlex.split('hellow wolrd "dsf sdf df" sdf\ sdf abc')
['hellow', 'wolrd', 'dsf sdf df', 'sdf sdf', 'abc']

            Then we can match left to right to find things in the schema node.
            it's going to be slower but more robust

            """)

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
