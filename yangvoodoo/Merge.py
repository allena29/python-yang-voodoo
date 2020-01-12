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

    def _expand_list_instances(self):
        """
        Given a list of all possible data nodes from the schema and a predicate map, returns
        an expanded list with all list elements in the right place.
        """

        results = self._get_all_data_paths()
        for (xpath, predicates, contianer) in results:
            if predicates:
                this_list_xpath = xpath + predicates
                this_list = []
                for i in range(self.predicate_path_count[this_list_xpath]):
                    this_list.append(next(results))

                for list_element in self.predicate_map[this_list_xpath]:
                    yield self._build_result(list_element)
                    for (this_list_field, _, _) in this_list:
                        yield self._build_result(this_list_field.replace(this_list_xpath, list_element))
            else:
                yield self._build_result(xpath)

    def _build_result(self, xpath):
        val = None
        if not xpath[-1] == ']':
            tmp = list(self.libyang_data.get_xpath(xpath))
            if tmp:
                val = tmp[0].value
        return (xpath, val)

    def _build_map_of_predicates(self):
        """
        After we have _get_all_data_paths we simply just have to expand the predicates.

        This intermediate function will do a gets_xpath() to find the list elements that
        exist in the list, and will then work out how many paths belong to that list.
        """
        last_predicate = None
        self.predicate_map = {}
        self.predicate_path_count = {}
        i = 0
        for (path, predicates, _) in self._get_all_data_paths():
            if predicates:
                combined_path = path + predicates
                # print(combined_path)
                self.predicate_map[combined_path] = []
                self.predicate_path_count[combined_path] = 0
                last_predicate = combined_path
                for xpath in self.libyang_data.gets_xpath(path):
                    self.predicate_map[combined_path].append(xpath)
            if last_predicate and path.startswith(last_predicate):
                self.predicate_path_count[last_predicate] += 1

            i = i + 1

    def _get_all_data_paths(self):
        """
        This method does nothing more than get all data_paths based upon a schema.
        It returns a generator of tuples.
            ( path to node or list element, predicates).

        This uses the schema only.
        """
        top_nodes = self.libyang_ctx.find_path(f'/{self.yang_model}:*')
        for top_node in top_nodes:
            yield self._get_result(top_node)
            if self._is_containing_node(top_node):
                for node in self.libyang_ctx.find_path(top_node.schema_path()+"//*"):
                    yield self._get_result(node)

    @staticmethod
    def _is_containing_node(node):
        return node.nodetype() in (Types.LIBYANG_NODETYPE['CONTAINER'], Types.LIBYANG_NODETYPE['LIST'])

    @staticmethod
    def _get_result(node):
        """
        Split a node's data_path into it's list_element and predicates
        """
        data_path = node.data_path()
        if node.nodetype() == Types.LIBYANG_NODETYPE['CONTAINER']:
            return (data_path, None, node)
        data_path = node.data_path()
        if hasattr(node, 'keys'):
            keys = list(node.keys())
            list_element_path = f"[{keys[0].name()}='%s']"
            predicates = data_path.find(list_element_path)
            return (data_path[0: predicates], data_path[predicates:], node)
        return (data_path, None, node)
    #
    # def _expand_list(self, xpath):
    #     if 1 == 0:
    #         yield ''
    #     for list_xpath in self.predicate_map:
    #         if list_xpath in xpath:
    #             for list_element_xpath in self.predicate_map[list_xpath]:
    #                 yield xpath.replace(list_xpath, list_element_xpath)
