import sys
import libyang

from yangvoodoo.Common import Utils
from yangvoodoo.Merge import DataSchema
from yangvoodoo import Types


print("""
      <link rel="stylesheet" type="text/css" href="voodoo-form.css" />

<body bgcolor=black><font color=white>

""")


class FormGenerator:

    def __init__(self, yang_model, data_format=None, data=[], yang_location=None, log=None):
        """
        Given a yangmodel provide a html form.
            :param yangmodel:     Name of a yangmodel
            :param dataformat:    Optional dataform, `xml` or `json`
            :param data:          list of data files to build the data tree.
            :param yang_location:  Optional path to search for a yang tree.
        """
        if not log:
            log = Utils.get_logger('FormGenerator')
        self.log = log
        self.schema = DataSchema(yang_model, data_format, data, yang_location=yang_location)
        self.results = list(self.schema.process())

    def build(self):
        print('<div class="voodoo-form-widget">')
        self.create_skeleton_structure()
        print('final untrace')
        print(self._untrace())
        print('</div>')

    def create_skeleton_structure(self):
        """
        This method builds static components which are not able to dynamically add, this gives
        us a skeleton outline structure.
        """
        self.trace = ['', '', '']
        for (xpath, value, node, widget_id) in self.results:
            self._render_widget(xpath, value, node, widget_id)
            pass

    def _render_widget(self, xpath, value, node, widget_id):
        safe_xpath = WebRenderUtils._get_quote_safe_name(xpath)
        print(self._indent() + self._untrace(node, xpath, widget_id))
        print(self._indent() + self._trace(node, xpath, widget_id))

        print(self._indent() + f'  <div id="widget_{safe_xpath}">')
        print(self._indent() + f'    <span class="voodoo-form-label">{node.name()}</span>')

        if node.nodetype() == Types.LIBYANG_NODETYPE['LEAF']:
            print(self._indent() + '  '+WebRenderUtils.render_input_field(safe_xpath, value, node))

        print(self._indent() + f'  </div> <!-- end {xpath} -->')
        print()

    def _trace(self, node, xpath, widget_id):
        # if node.nodetype() in (Types.LIBYANG_NODETYPE['CONTAINER'], Types.LIBYANG_NODETYPE['LIST']):
        #     sys.stderr.write('adding: %s\n' % (xpath))
        #     self.trace.append(widget_id)
        #     return f'<div id="tupperware_{xpath}" class="containing-node">'
        # return ''

        if widget_id == self.trace[-1]:
            sys.stderr.write(f'{xpath} belongs to existing {widget_id}\n')
            return ''
        else:
            sys.stderr.write(f'{xpath} requires a new widget_id {widget_id}\n')
            self.trace.append(widget_id)
            return f'<div id="tupperware_{xpath}" class="containing-node"> <!-- widget id {widget_id} -->'

    def _untrace(self, node=None, xpath=None, widget_id=None):
        # sys.stderr.write('tip: %s %s\n' % (self.trace[-1], xpath))
        sys.stderr.write(f'   untrace:  {widget_id} {xpath} {self.trace}\n')
        if widget_id != self.trace[-1]:
            removed = self.trace.pop()
            return f'</div> <!-- close tupperware {removed} -->'
        return ''

    def _indent(self):
        return ' '*len(self.trace)*2


class WebRenderUtils:

    @staticmethod
    def _get_quote_safe_name(input_string):
        return input_string.replace('"', '&quot;')

    @staticmethod
    def render_input_field(xpath, value, node):
        leaf_type = node.type().base()
        if leaf_type == Types.LIBYANG_LEAF_TYPES['BOOLEAN']:
            return WebRenderUtils._render_input_field_checkbox(xpath, value, node)
        if value is None:
            value = ''
        return f'<input type="text" name="{xpath}" value="{value}">'

    @staticmethod
    def _render_input_field_checkbox(xpath, value, node):
        checked = ''
        if value:
            checked = 'CHECKED'
        return f'<input type="checkbox" name="{xpath}" value="{value}" {checked}>'
