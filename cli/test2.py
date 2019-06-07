from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.styles import Style
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError
from prompt_toolkit import PromptSession
#from prompt_toolkit.history import FileHistory
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

html_completer = WordCompleter(['html>', 'body>', 'head>', 'title>'])


class NumberValidator(Validator):
    def validate(self, document):
        text = document.text

        if text and not text.isdigit():
            i = 0

            # Get index of fist non numeric character.
            # We want to move the cursor here.
            for i, c in enumerate(text):
                if not c.isdigit():
                    break

            raise ValidationError(message='This input contains non-numeric characters',
                                  cursor_position=i)


style = Style.from_dict({
    # User input (default text).
    '':          '#ff0066',

    # Prompt.
    'username': '#884444',
    'at':       '#00aa00',
    'colon':    '#0000aa',
    'pound':    '#00aa00',
    'host':     '#00ffff bg:#444400',
    'path':     'ansicyan underline',
})

message = [
    ('class:username', 'john'),
    ('class:at',       '@'),
    ('class:host',     'localhost'),
    ('class:colon',    ':'),
    ('class:path',     '/user/john'),
    ('class:pound',    '# '),
]

session = PromptSession()

class ValidateCommands(Validator):
    def validate(self, document):
        print('a')

session._ourcommands = WordCompleter(['show', 'configure'])

while 1:
    try:
        text = session.prompt(message, style=style, completer=session._ourcommands, complete_while_typing=True, validate_while_typing=True, auto_suggest=AutoSuggestFromHistory())
        print('got', text)	
    except KeyboardInterrupt:
        continue
    except EOFError:
        break

#text = prompt(message, style=style, completer=html_completer, complete_while_typing=True, validator=NumberValidator(), validate_while_typing=True, auto_suggest=AutoSuggestFromHistory())
#print('got', text)

