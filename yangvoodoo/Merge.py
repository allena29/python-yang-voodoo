import sys
import hashlib
import libyang

from yangvoodoo.Common import Utils
from yangvoodoo import Types


class DataSchema:

    """
    Merge a schema and data tree to provide a list of XPATH's.
    """

    def __init__(self, yang_model,  data_format=None, data=[], yang_location=None, log=None):
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
        self.output_fh = sys.stdout
        self.last_containing_struct = []
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
        self._build_map_of_predicates()
        for result in self._expand_list_instances():
            yield result

    def _expand_list_instances(self):
        """
        Given a list of all possible data nodes from the schema and a predicate map, returns
        an expanded list with all list elements in the right place.
        """

        results = self._get_all_data_paths()
        for (xpath, predicates, node, hash) in results:
            if predicates:
                this_list_xpath = xpath + predicates
                this_list = []
                for i in range(self.predicate_path_count[this_list_xpath]):
                    this_list.append(next(results))

                for list_element in self.predicate_map[this_list_xpath]:
                    yield self._build_result(list_element, node, hash)
                    for (this_list_field, _, sub_node, sub_hash) in this_list:
                        yield self._build_result(this_list_field.replace(this_list_xpath, list_element), sub_node, sub_hash)
            else:
                yield self._build_result(xpath, node, hash)

    def _build_result(self, xpath, node, hash):
        val = None
        if not xpath[-1] == ']':
            tmp = list(self.libyang_data.get_xpath(xpath))
            if tmp:
                val = tmp[0].value
        return (xpath, val, node, hash)

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
        for (path, predicates, _, _) in self._get_all_data_paths():
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
        self.structures = {'da39a3ee5e6b4b0d3255bfef95601890afd80709': ''}

        top_nodes = self.libyang_ctx.find_path(f'/{self.yang_model}:*')
        for top_node in top_nodes:
            yield self._get_result(top_node)
            if self._is_containing_node(top_node):
                for node in self.libyang_ctx.find_path(top_node.schema_path()+"//*"):
                    yield self._get_result(node)

    def _is_containing_node(self, node):
        return node.nodetype() in (Types.LIBYANG_NODETYPE['CONTAINER'], Types.LIBYANG_NODETYPE['LIST'])

    def _get_result(self, node):
        """
        Split a node's data_path into it's list_element and predicates
        """
        schema_hash = self._get_hash_of_structure(node)
        data_path = node.data_path()
        if node.nodetype() == Types.LIBYANG_NODETYPE['CONTAINER']:
            return (data_path, None, node, schema_hash)
        data_path = node.data_path()

        if hasattr(node, 'keys'):
            keys = list(node.keys())
            list_element_path = f"[{keys[0].name()}='%s']"
            predicates = data_path.find(list_element_path)
            return (data_path[0: predicates], data_path[predicates:], node, schema_hash)
        return (data_path, None, node, schema_hash)

    def _get_hash_of_structure(self, node):
        """
        Return a hash of the schema structure- this assumes if we are not a container we just
        strip the last node name off.

            38f697830d29188847b6d756cb7239e20e22f043 /form:toplevel-list
            b15871681f832be39030a7b142f2b54b8484f525 /form:toplevel-list/form:two
            6b87dab11d546afe2faa86a6d2cb31e38d266977 /form:composite-list
            933b7ea5da997fb759732943f35dca59e5925c30 /form:composite-list/form:two
            dbefc2a2fa24e6415280852de37e40df16b9a49a /form:form-section
            d84423181e0f6d9ee9fe260e1ccf2227d2e71cd1 /form:form-section/form:abc
            1c286d6bb9056c56f57445e6418adff0e238c75e /form:form-section/form:abc/form:b
            7d906e4cc4deae3a81743ddd13da623566f59db5 /form:form-section/form:abc/form:b/form:xyz
            ad1361eea6dc1b40c6bea4b36d783cf3223d04eb /form:form-section/form:abc/form:b/form:xyz/form:y
            54a927f48a4409c13e72d483f72a31c38de149ce /form:footer-form
        """
        schema_path = node.schema_path()
        containing_node = self._is_containing_node(node)
        if containing_node:
            hash = hashlib.sha1(schema_path.encode('utf-8')).hexdigest()
            self.structures[hash] = schema_path

        schema_path = schema_path[:schema_path.rfind('/')]
        hash = hashlib.sha1(schema_path.encode('utf-8')).hexdigest()
        return hash
