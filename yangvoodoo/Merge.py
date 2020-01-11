import sys
import libyang

from yangvoodoo.Common import Utils
from yangvoodoo import Types


class DataSchema:

    """
    Merge a schema and data tree to provide a list of XPATH's.
    """

    def __init__(self, yang_model, entry_node,  data_format=None, data=[], yang_location=None, log=None):
        """
        Given a yangmodel provide a html form.
            :param yangmodel:     Name of a yangmodel
            :param dataformat:    Optional dataform, `xml` or `json`
            :param data:          list of data files to build the data tree.
            :param yang_location:  Optional path to search for a yang tree.
        """
        if not log:
            log = Utils.get_logger('Merge')
        self.log = log

        self.libyang_ctx = libyang.Context(yang_location)
        self.libyang_ctx.load_module(yang_model)
        self.libyang_data = libyang.DataTree(self.libyang_ctx)
        self.yang_model = yang_model
        self.entry_node = entry_node
        self.output_fh = sys.stdout
        self.widgets = {}
        self.data_format = 1
        if data_format == 'json':
            self.data_format = 2
        self.data_tree_exists = False
        for data_file in data:
            self._load(data_file)

    def _load(self, data_file):
        if self.data_tree_exists:
            method = 'merges'
        else:
            method = 'loads'
            self.data_tree_exists = True
        with open(data_file) as fh:
            getattr(self.libyang_data, method)(fh.read(), self.data_format)

    def process(self):
        """
        libyang doesn't do a recursive search on the path /module:*//*, this means we
        have a limitation of specifying the first node we want to search
        """
        self.yang_lists = [('__root',)]
        self.list_predicates = []

        top_nodes = self.libyang_ctx.find_path(f'/{self.yang_model}:*')
        # top_nodes = self.libyang_ctx.find_path(f'/{self.yang_model}:{self.entry_node}//*')
        for top_node in top_nodes:
            if self._is_containing_node(top_node):
                for result in self._process_containing_nodes(top_node):
                    yield result

                for node in self.libyang_ctx.find_path(top_node.schema_path()+"//*"):
                    if self._is_containing_node(node):
                        self._process_containing_nodes(node)
                    else:
                        data_path = self._get_data_path(node)
                        yield (data_path, node.schema_path(), self._return_value(data_path))
            else:
                # Non Containing Nodes
                data_path = self._get_data_path(top_node)
                yield (data_path, top_node.schema_path(), self._return_value(data_path))

    def _return_value(self, data_path):
        data = list(self.libyang_data.get_xpath(data_path))
        if data:
            return data[0].value
        return None

    @staticmethod
    def _is_containing_node(node):
        return node.nodetype() in (Types.LIBYANG_NODETYPE['CONTAINER'], Types.LIBYANG_NODETYPE['LIST'])

    def _process_containing_nodes(self, node):
        if node.nodetype() == Types.LIBYANG_NODETYPE['LIST']:
            self._process_list(node)
        print(node, 'is containing node')
        if 1 == 0:
            yield None

    def _process_list(self, node):
        print()
        print(self.yang_lists, '<<< yang lists')
        print(self.list_predicates, "<<<< list predicates")

        schema_path = node.schema_path()
        # yang_lists
        #  - first entry is a dummy entry
        #  - other entries is a tuple, path and number  of entries
        if not self.yang_lists[-1][0].startswith(schema_path):
            keys = list(node.keys())
            print('we have the following keys')
            self.yang_lists.append((node.schema_path, keys))

            list_element_path = schema_path.replace("[%s='%%s']" % (keys[0]), '')
            print(list_element_path, '<<< list element_path')

            for xpaths in self.libyang_data.gets_xpath(list_element_path):
                print(xpaths)
            print('new list', node.data_path())

        else:
            d = 5/0
            print('existing list')

        print(dir(node))

        print(list(node.keys()))
        print('process list', node)

    def _get_data_path(self, node):
        data_path = node.data_path()
        print('before predicates', data_path)
        print('list_predicates', self.list_predicates)
        try:
            return data_path.replace('%s', '{}').format(*self.list_predicates)
        except IndexError:
            raise
            raise ValueError('problem getting data path\n%s\n%s' % (data_path, str(self.list_predicates)))
