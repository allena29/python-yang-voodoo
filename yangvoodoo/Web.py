import sys
import libyang

from yangvoodoo.Common import Utils
from yangvoodoo.Merge import DataSchema
from yangvoodoo import Types


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
        print('<div class="widget">')
        self.create_skeleton_structure()
        print('</div>')

    def create_skeleton_structure(self):
        """
        This method builds static components which are not able to dynamically add, this gives
        us a skeleton outline structure.
        """

        for (xpath, value, node, widget_id) in self.results:
            # if widget_id == widget:
            if '%' in node.data_path():
                continue
            print(f"  <span class='label'>{node.name()}</span>")
            print(self.static_widget(node, xpath, value))
            print("<br>")

    def static_widget(self, node, xpath, value):
        if node.nodetype() == Types.LIBYANG_NODETYPE['CONTAINER']:
            return ""

        if node.nodetype() == Types.LIBYANG_NODETYPE['LEAF']:
            if value is None:
                value = ''
            widget = f"<textarea name='{xpath}' rows=1 cols=40>{value}</textarea>"
        else:
            widget = 'not supported widget for node %s/%s' % (node, node.nodetype())

        return widget
