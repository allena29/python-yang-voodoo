import sys
import libyang
from lxml.etree import Element
from yangvoodoo.Common import Utils
from yangvoodoo.Merge import DataSchema
from yangvoodoo import Types
from xml.etree import ElementTree
from xml.dom import minidom


def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
#
# print("""
#       <link rel="stylesheet" type="text/css" href="voodoo-form.css" />
#
# <body bgcolor=black><font color=white>
#
# """)


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
        map = {}

        doc = Element('html')

        style = Element('link')
        style.attrib['rel'] = 'stylesheet'
        style.attrib['type'] = 'text/css'
        style.attrib['href'] = 'voodoo-form.css'
        doc.append(style)

        voodooform = Element('div')
        voodooform.attrib['id'] = 'voodoo-form-widget'
        doc.append(voodooform)

        map['/'] = RenderFormTools.create_containing_section(voodooform, None, '/')

        for (xpath, node, parent, value) in self.results:
            if node.nodetype() in (Types.LIBYANG_NODETYPE['CONTAINER'], Types.LIBYANG_NODETYPE['LIST']):
                map[xpath] = RenderFormTools.create_containing_section(map[parent], node, xpath)
            if node.nodetype() == Types.LIBYANG_NODETYPE['LEAF']:
                RenderFormTools.create_field(map[parent], node, xpath, value)
        #     map[parent] = Element("div")
        #     map[parent].attrib['class'] = 'voodoo-containing-node'
        #     voodooform.append(map[parent])
        #
        #     container_title = Element("span")
        #     container_title.attrib['class'] = 'voodoo-form-title-text'
        #     container_title.text = node.name()
        #     map[parent].append(container_title)

        print(prettify(doc))


class RenderFormTools:

    @staticmethod
    def create_field(parent, node, path, value):

        field_section = Element("div")
        field_section.attrib['class'] = 'voodoo-field-section'
        field_section.attrib['id'] = f'vff_{path}'     # vf - for voodoo field
        parent.append(field_section)

        title = Element("span")
        title.attrib['class'] = 'voodoo-input-title-text'
        title.text = node.name() + '  type' + str(node.type().base())
        field_section.append(title)

        input = Element("input")
        input.attrib['name'] = f'vf_{path}'
        if value:
            input.attrib['value'] = value
        field_section.append(input)

    @staticmethod
    def create_containing_section(parent, node, path):

        containing_section = Element("div")
        containing_section.attrib['class'] = 'voodoo-containing-section'
        containing_section.attrib['id'] = f'vcs_{path}'     # vcs - for voodoo containing seciton
        parent.append(containing_section)

        if node and node.nodetype() == Types.LIBYANG_NODETYPE['LIST']:
            container_title = Element("span")
            container_title.attrib['class'] = 'voodoo-form-title-text'
            container_title.text = 'LIST' + path + str(list(node.keys()))
            containing_section.append(container_title)

        if node and node.nodetype() == Types.LIBYANG_NODETYPE['CONTAINER']:
            container_title = Element("span")
            container_title.attrib['class'] = 'voodoo-form-title-text'
            container_title.text = node.name() + path
            containing_section.append(container_title)

        return containing_section

        # print(Utils.convert_path_to_nodelist(xpath), Utils.extract_all_keys(xpath))

        #
        #         print('<div class="voodoo-form-widget">')
        #         self.create_skeleton_structure()
        #         print('final untrace')
        #         print(self._untrace())
        #         print('</div>')
        #
        #     def create_skeleton_structure(self):
        #         """
        #         This method builds static components which are not able to dynamically add, this gives
        #         us a skeleton outline structure.
        #         """
        #         self.trace = ['', '', '']
        #         for (xpath, value, node, widget_id) in self.results:
        #             self._render_widget(xpath, value, node, widget_id)
        #             pass
        #
        #     def _render_widget(self, xpath, value, node, widget_id):
        #         safe_xpath = WebRenderUtils._get_quote_safe_name(xpath)
        #         print(self._indent() + self._untrace(node, xpath, widget_id))
        #         print(self._indent() + self._trace(node, xpath, widget_id))
        #
        #         print(self._indent() + f'  <div id="widget_{safe_xpath}">')
        #         print(self._indent() + f'    <span class="voodoo-form-label">{node.name()}</span>')
        #
        #         if node.nodetype() == Types.LIBYANG_NODETYPE['LEAF']:
        #             print(self._indent() + '  '+WebRenderUtils.render_input_field(safe_xpath, value, node))
        #
        #         print(self._indent() + f'  </div> <!-- end {xpath} -->')
        #         print()
        #
        #     def _trace(self, node, xpath, widget_id):
        #         # if node.nodetype() in (Types.LIBYANG_NODETYPE['CONTAINER'], Types.LIBYANG_NODETYPE['LIST']):
        #         #     sys.stderr.write('adding: %s\n' % (xpath))
        #         #     self.trace.append(widget_id)
        #         #     return f'<div id="tupperware_{xpath}" class="containing-node">'
        #         # return ''
        #
        #         if widget_id == self.trace[-1]:
        #             sys.stderr.write(f'{xpath} belongs to existing {widget_id}\n')
        #             return ''
        #         else:
        #             sys.stderr.write(f'{xpath} requires a new widget_id {widget_id}\n')
        #             self.trace.append(widget_id)
        #             return f'<div id="tupperware_{xpath}" class="containing-node"> <!-- widget id {widget_id} -->'
        #
        #     def _untrace(self, node=None, xpath=None, widget_id=None):
        #         # sys.stderr.write('tip: %s %s\n' % (self.trace[-1], xpath))
        #         sys.stderr.write(f'   untrace:  {widget_id} {xpath} {self.trace}\n')
        #         if widget_id != self.trace[-1]:
        #             removed = self.trace.pop()
        #             return f'</div> <!-- close tupperware {removed} -->'
        #         return ''
        #
        #     def _indent(self):
        #         return ' '*len(self.trace)*2
        #
        #
        # class WebRenderUtils:
        #
        #     @staticmethod
        #     def _get_quote_safe_name(input_string):
        #         return input_string.replace('"', '&quot;')
        #
        #     @staticmethod
        #     def render_input_field(xpath, value, node):
        #         leaf_type = node.type().base()
        #         if leaf_type == Types.LIBYANG_LEAF_TYPES['BOOLEAN']:
        #             return WebRenderUtils._render_input_field_checkbox(xpath, value, node)
        #         if value is None:
        #             value = ''
        #         return f'<input type="text" name="{xpath}" value="{value}">'
        #
        #     @staticmethod
        #     def _render_input_field_checkbox(xpath, value, node):
        #         checked = ''
        #         if value:
        #             checked = 'CHECKED'
        #         return f'<input type="checkbox" name="{xpath}" value="{value}" {checked}>'
