#!/usr/bin/env python3
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import prompt


import yangvoodoo
# import argparse
from logsink import LogWrap
import sys
import time
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.completion import Completer, Completion


class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        """
        document - https://python-prompt-toolkit.readthedocs.io/en/1.0.15/pages/reference.html#module-prompt_toolkit.document
           has text
        """
        global log, state_object
        log.info('get_completions: %s' % (document.text))
        last_part = document.text.split(' ')[-1]

        for child in state_object.current_node._children():
            if child[0:len(last_part)] == last_part:

                yield Completion(
                    child[len(last_part):] + " ", start_position=0,
                    display=HTML('<b>%s</b> ' % (child)),
                    # style='bg:ansiyellow')
                )


class MyValidator(Validator):
    def validate(self, document):
        global log, state_object
        last_part = document.text.split(' ')[-1]
        log.info('validate: %s  --- %s/%s - %s' % (document.text, len(document.text), state_object.valid_position, last_part))
        for child in state_object.current_node._children():
            # log.info('... this is valid %s' % (child))
            if child[0:len(last_part)] == last_part:
                state_object.valid_position = len(document.text)
                return True

        sys.stdout.write("\a")
        state_object.buffer.delete_before_cursor(1)
        raise ValidationError(message='This input contains non-numeric characters',
                              cursor_position=0)


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

    def __init__(self):
        self.conf_mode = 0
        self.first_command = None
        self.session = yangvoodoo.DataAccess()
        self.session.connect("integrationtest", yang_location="../yang")
        self.root = self.session.get_node()
        self.current_node = self.root

        self.valid_position = 0


class cli:

    def __init__(self, state_object):
        self.log = LogWrap("cli")
        self.log.info("CLI Started")
        self.user = "steg"
        self.host = "localhost"
        self.exit = False

        self.state_object = state_object

        self.prompt = self._get_prompt_session()
        print(self.prompt)
        print(self.prompt.default_buffer)
        self.state_object.buffer = self.prompt.default_buffer

    def _get_prompt_session(self):
        return PromptSession()

    def _get_completer(self):
        return WordCompleter(['set ', 'show '])

    def _prompt_and_wait_for_cli(self):
        prompt = "%s@%s> " % (self.user, self.host)

        return self.prompt.prompt(prompt,
                                  bottom_toolbar=formats.bottom_toolbar,
                                  completer=MyCustomCompleter(),
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
                    x = self._prompt_and_wait_for_cli()

                    print(x)
                except KeyboardInterrupt:
                    pass
                except EOFError:
                    break
        except KeyboardInterrupt:
            pass
        except EOFError:
            pass


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
    c.loop()
#
