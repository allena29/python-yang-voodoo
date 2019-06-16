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
            options = state_object.get_completions(document, validator=False)

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

        if not state_object.current_command:
            options = state_object.get_command_completions(document)
        else:
            options = state_object.get_completions(document)

        for option in options:
            return True

        if not document.text[-1] == ' ':
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
    CONF_COMMANDS = [('set ', 1), ('delete ', 1), ('exit', 1), ('validate', 1), ('commit', 1)]
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
        #self.go_to_parent = [-1]
        #self.valid_position = 0
        #self.last_cursor_position = -1
        #self.stop_completions_and_validation = False
        #self.restart_completions_at = 1
        self.current_command = None
        self.stop_completions_and_validation = False

    def get_command_completions(self, document, validator=True):
        if validator:
            log.info("Consisdering %s-command  for __%s__", self.mode, document.text)

        completions = self.OPER_COMMANDS
        if self.mode == 1:
            completions = self.CONF_COMMANDS

        for (completion, visibility) in completions:
            if completion[0:len(document.text)] == document.text:
                if not (visibility == 0 and not validator):
                    yield (completion[len(document.text):], completion)

    def get_completions(self, document, hide_optional=False):
        """
        hide_optional - when used by a completer will be set to true, when used by a validator will be set to false.
        """

        return []

    def old_get_completions(self, document, hide_optional=False):
        global log
        parts = self._get_space_separated_values(document.text)

        if len(parts) == 0:
            # log.info("No parts")
            return
        log.info("%s parts-1=%s len(text)=%s gotoparent=%s repr(curretNode)=%s stop=%s", document.text,
                 parts[-1], len(document.text), self.go_to_parent, repr(self.current_node),            self.stop_completions_and_validation
                 )

        space_count = len(parts)
        # log.info("parts... %s (%s)" % (parts, space_count))
        last_part = '' + parts[-1]

        if self.restart_completions_at > 0 and len(document.text) == self.restart_completions_at and len(document.text) < self.last_cursor_position:
            # log.info('now should valid and complete')
            self.stop_completions_and_validation = False

        elif len(document.text)+1 == self.go_to_parent[-1] and len(document.text) < self.last_cursor_position:
            # only do this if we are going backwards and we have gone far enough back.
            parent_node = self.current_node._parent
            # log.info('Hit the trap... we need to go to our parent node... will be %s', repr(parent_node))
            self.current_node = parent_node
            self.go_to_parent.pop()
        elif document.text[-1] == ' ' and len(parts) > 1 and len(document.text) > self.go_to_parent[-1]+1:
            # The logic here is right - it would be nice if we need need to do quite as much work to track the up
            # and down bits.
            # log.info('transitioning modes.....%s.....%s...%s..', parts[-1], len(document.text), self.go_to_parent)
            try:
                new_node = self.current_node[parts[-1]]
                self.go_to_parent.append(len(document.text) - 1)
                # log.info('new node.... %s', repr(new_node))
                self.current_node = new_node
                # We need to track where we switch ed
            except Exception:
                self.stop_completions_and_validation = True
                self.restart_completions_at = len(document.text)+1
                log.info('this isnt a containngnnnode %s', len(document.text))

        # log.info('get completions: _%s_%s_', document.text, last_part)
        if (space_count > 2 and self.mode == 0) or (space_count > 1 and self.mode == 1):
            if self.stop_completions_and_validation:
                completions = []
            else:
                completions = self.current_node._children()
        elif self.mode == 0 and space_count == 1:
            completions = self.OPER_COMMANDS2
        elif self.mode == 0:
            completions = self.OPER_COMMANDS
        else:
            completions = self.CONF_COMMANDS

        self.last_cursor_position = len(document.text)
        for completion in completions:
            if isinstance(completion, tuple):
                (child, visibility) = completion
            else:
                child = completion
                visibility = True

            if child[0:len(last_part)] == last_part:
                # TODO: ideally here we will know if something is a terminating node
                # e.g. bronze, isn't a presence container so it makes sesnse to complete that as 'bronze '
                # deep is a terminating leaf node that takes a value so it makes sense to complete that as 'deep '
                # Potentially a little deviation frmo Juniper CLI syntax might be to always have '=' for leaf values.
                # No matter how it's rendered on the CLI we need to know the information.
                state_object.valid_position = len(document.text)
                if not (visibility == 0 and hide_optional):
                    yield (child[len(last_part):], child)

        # if len(completions) == 1:
            # log.info("here might be a good idea to know if we are dealing with a leaf....")
            # it doesn't make sense to try before we are down to on ematch.

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
                        self.state_object.mode = 0
                        print("\n[ok][%s]" % (formats.get_time()))
                        self.state_object.current_node = self.state_object.root
                        self.state_object.go_to_parent = [-1]
                        self.state_object.stop_completions_and_validation = False
                        self.state_object.restart_completions_at = -1
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
            self.state_object.mode = 1
            self.state_object.current_node = self.state_object.root
            self.state_object.go_to_parent = [-1]
            self.state_object.stop_completions_and_validation = False
            self.state_object.restart_completions_at = -1
            return True

    def _process_conf_command(self, cmd):
        self.log.info('processing conf _%s_', cmd)
        if cmd == "exit":
            print("\n[ok][%s]" % (formats.get_time()))
            self.state_object.mode = 0
            self.state_object.current_node = self.state_object.root
            self.state_object.go_to_parent = [-1]
            self.state_object.stop_completions_and_validation = False
            self.state_object.restart_completions_at = -1
            return True
        else:
            self.log.info('operate on voodoo node: %s', self.state_object.current_node)
            # here we don't have the correct voodoo node out of the box
            # in the example 'set cli a apple <X>' we get the voodoo node a
            parts = state._get_space_separated_values(cmd)
            self.log.info('parts %s', str(parts))
            self.log.info('parts-2  %s', parts[-2])
            self.log.info('our node now %s', our_node)
            self.log.info('new node: %s of type %s', our_node, our_node._NODE_TYPE)


# class cruxli:
#
#     def __init__(self, host='localhost', port='830',
#                  username='netconf', password='netconf'):
#
#         FORMAT = "%(asctime)-15s - %(name)-20s %(levelname)-12s  %(message)s"
#         logging.basicConfig(level=logging.DEBUG, format=FORMAT)
#         self.log = logging.getLogger('cli')
#
#         self.host = host
#         self.port = port
#         self.username = username
#         self.password = password
#         self.cliformat = None
#         self.yang_manager = Yang.Yang()
#
#     def reset_cli(self):
#         self.mode = 0
#         self.exit = False
#
#     def start_cli_session(self):
#         self.reset_cli()
#         self.netconf = self._connect_netconf(self.host, self.port, self.username, self.password)
#         self.yang_manager.negotiate_netconf_capabilities(self.netconf)
#
#     def __del__(self):
#         self._disconnect_netconf()
#
#     def _disconnect_netconf(self):
#         pass
#
#     def attach_formatter(self, formatter):
#         self.cliformat = formatter
#
#     def _connect_netconf(self, host, port, username, password):
#         """
#         Connect to a given NETCONF host and verify that it has the CRUX
#         YANG module installed.
#
#         If a NETCONF server does indeed have the correct module installed
#         it shuld provide a list of YANG Modules which are to be used with
#         this CLI engine.
#
#         <?xml version="1.0" encoding="UTF-8"?>
#          <data xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"
#                xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0">
#           <crux-cli xmlns="http://brewerslabng.mellon-collie.net/yang/crux">
#            <modules>
#             <module>brewerslab</module>
#            </modules>
#            <modules>
#             <module>integrationtest</module>
#            </modules>
#           </crux-cli>
#          </data>
#         """
#
#         netconf = manager.connect(host=host, port=port,
#                                   username=username, password=password,
#                                   hostkey_verify=False, allow_agent=False,
#                                   look_for_keys=False,
#                                   unknown_host_cb=lambda x: True)
#
#         return netconf
#
#     def _process_module(self, cm):
#         module = None
#         namespace = None
#         revision = 'unspecified'
#         tops = []
#         for x in cm.getchildren():
#             if x.tag == self.CRUX_NS + "module":
#                 module = x.text
#             if x.tag == self.CRUX_NS + "namespace":
#                 namespace = x.text
#             if x.tag == self.CRUX_NS + "revision":
#                 revision = x.text
#             if x.tag == self.CRUX_NS + "top-level-tags":
#                 for t in x.getchildren():
#                     if t.tag == self.CRUX_NS + "tag":
#                         tops.append(t.text)
#
#         if module and namespace:
#             if namespace not in self.netconf_capa:
#                 raise ValueError('NETCONF server does expose %s %s' % (module,
#                                                                        namespace))
#
#         self.cli_modules[module] = namespace
#
#         return (module, namespace, revision, tops)
#
#     def _process_modules(self, netconf, crux_modules):
#         """
#         Process the list of modules given an XML structure representing the
#         configuration of /crux-cli
#         """
#         for cm in crux_modules.getchildren():
#             (module, namespace, revision, tops) = self._process_module(cm)
#
#             for t in tops:
#                 if t in self.yang_manager.top_levels:
#                     raise ValueError("Top-level tag %s is already registered to another namespace")
#                 self.log.debug("Registered new top-level tag %s to %s" % (t, namespace))
#                 self.yang_manager.top_levels[t] = namespace
#
#             self.yang_manager.cache_schema(netconf, module, namespace, revision)
#
#         for ym in self.yang_manager.netconf_capa:
#             print("We need schema for %s" % (ym))
#
#     def process_cli_line(self, line):
#         self.log.debug('Oper line into us: %s' % (line))
#         if line[0:4] == "conf":
#             self.log.debug("Switching into configuration mode")
#             self.mode = 1
#         elif line[0:4] == "show":
#             self.log.debug("Show operation state")
#         elif line[0:4] == "exit":
#             self.log.debug("Exit required")
#             self.exit = True
#         elif line == "":
#             pass
#         else:
#             self.cliformat.opermode_error(line)
#
#     def process_config_cli_line(self, line):
#         self.log.debug("Config line to use: %s" % (line))
#         if line[0:4] == "exit":
#             self.log.debug("Switching into operational mode")
#             self.mode = 0
#
#     def get_and_process_next_command(self):
#         if self.mode:
#             self.process_config_cli_line(self.cliformat.configmode_prompt())
#         else:
#             self.process_cli_line(self.cliformat.opermode_prompt())
#
#     def loop(self):
#         try:
#             self.process_cli_line(self.cliformat.welcome())
#             while not self.exit:
#                 try:
#                     self.get_and_process_next_command()
#                 except KeyboardInterrupt:
#                     pass
#                 except EOFError:
#                     break
#         except KeyboardInterrupt:
#             pass
#         except EOFError:
#             pass
#
#
# if __name__ == '__main__':
#     cli = cruxli()
#     cli.attach_formatter(cruxformat())
#     cli.start_cli_session()
#     cli.loop()


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
