import libyang
import logging
from lxml import etree
from yangvoodoo import Types, Errors
import re


class YangNode:

    """
    This object wraps together a libyang schema node and the real formed paths
    for further searching against libyang or setting/reading data from a backend
    datastore.

    This object is instantiated to avoid mis-caching the value path which will differ
    for every list-element.

    This object will be returned by get_schema_node_from_libyang()
    """

    def __init__(self, libyang_node, real_schema_path, real_data_path, parent_data_path):
        self.libyang_node = libyang_node
        self.real_data_path = real_data_path
        self.real_schema_path = real_schema_path
        self.parent_data_path = parent_data_path

    def __getattr__(self, attr):
        if attr in ('real_schema_path', 'real_data_path'):
            return getattr(self, attr)
        return getattr(self.libyang_node, attr)


class PlainObject:
    pass


class PlainIterator:

    def __init__(self, children):
        self.children = children
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.children) > self.index:
            self.index = self.index + 1
            return self.children[self.index-1]
        raise StopIteration


class IteratorToRaiseAnException:

    def __init__(self, children, error_at=-1, error_type=Exception):
        self.children = children
        self.index = 0
        self.error_at = error_at
        self.error_type = error_type

    def __iter__(self):
        return self

    def __next__(self):
        if self.error_at > -1 and self.index == self.error_at:
            raise self.error_type()
        if len(self.children) > self.index:
            self.index = self.index + 1
            return self.children[self.index-1]
        raise StopIteration


class Utils:

    LOG_INFO = logging.INFO
    LOG_DEBUG = logging.DEBUG
    LOG_SILENT = 99
    LOG_ERROR = logging.ERROR
    LOG_TRACE = 7
    LOG_CRAZY = 4

    LAST_LEAF_AND_PREDICTAES = re.compile(r"(.*/)([A-Za-z]+[A-Za-z0-9_:-]*)(\[.*\])$")
    PREDICATE_KEY_VALUES_SINGLE = re.compile(r"\[([A-z]+[A-z0-9_\-]*)='([^']*)'\]")
    PREDICATE_KEY_VALUES_DOUBLE = re.compile(r"\[([A-z]+[A-z0-9_\-]*)=\"([^\"]*)\"\]")
    FIND_KEYS = re.compile(r"\[([A-Za-z]+[A-Za-z0-9_-]*)=.*?\]")
    FIND_KEYS_AND_VALUES = re.compile(r"\[([A-Za-z]+[A-Za-z0-9_-]*)=['\"](.*?)['\"]\]")
    DROP_PREDICATES = re.compile(r"(.*?)([A-Za-z0-9_-]+\[.*?\])?/([A-Za-z0-9_-]*)")
    DROP_ALL_PREDICATES = re.compile(r"(\[.*?\])")
    SPLIT_XPATH = re.compile(r"([a-zA-Z0-9_-]*)(/?)((\[.*?\])*)?")
    XPATH_DECODER_V4 = re.compile(r"(([A-Za-z0-9_-]*:)?([A-Za-z0-9_-]+))((\[[A-Z0-9a-z_-]+\s*=\s*(?P<quote>['\"]).*?(?P=quote)\s*\])+)?")
    XPATH_MATCH_AFTER_LAST_PREDICATE = re.compile(r"^(.*?)(/[^\[\]]*)$")
    STARTING_A_PREDICATE = re.compile(r".*\[[a-z0-9A-Z_-]+\s*=\s*['\"]")
    ENDING_A_PREDICATE = re.compile(r".*['\"]\s*\]$")
    MODULE_AND_LEAF_REGEX = re.compile(r"/([A-Za-z0-9_-]+:)?([A-Za-z0-9_-]+)")

    @staticmethod
    def pretty_xmldoc(xmldoc):
        xmlstr = str(etree.tostring(xmldoc, pretty_print=True))
        return str(xmlstr).replace('\\n', '\n')[2:-1]

    @staticmethod
    def convert_path_to_schema_path(path, module):
        """
        This takes a valid data XPATH and converts it to a schema path, where
        every node is prefixed with the module name and the predicates are removed.

        /path/abc/def[g='sdf']/xyz/sdf[fdsf='fg']/zzz
        /module:path/module:abc/module:def/module:xyz/module:sdf/module:zzz
            ('', '', 'path')
            ('', '', 'abc')
            ('', '', 'def')
            ("[g='sdf']", '', 'xyz')
            ('', '', 'sdf')
            ("[fdsf='fg']", '', 'zzz')
        """
        if path[0:len(module)+2] == "/"+module+":":
            path = "/" + path[len(module)+2:]
        if path[-1] == "/":
            raise ValueError("Path is not valid as it ends with a trailing slash. (%s)" % (path))
        schema_path = ""
        parent_schema_path = ""
        for (_, _, path) in Utils.DROP_PREDICATES.findall(path):
            parent_schema_path = schema_path
            schema_path += "/" + module + ":" + path
        return schema_path, parent_schema_path

    @staticmethod
    def convert_path_to_value_path(path, module):
        """
        /path/abc/def[g='sdf']/xyz/sdf[fdsf='fg']/zzz
        /module:path/module:abc/module:def/module:xyz/module:sdf/module:zzz
            ('', '', 'path')
            ('', '', 'abc')
            ('', '', 'def')
            ("[g='sdf']", '', 'xyz')
            ('', '', 'sdf')
            ("[fdsf='fg']", '', 'zzz')
        """
        if path[0:len(module)+2] == "/"+module+":":
            path = "/" + path[len(module)+2:]
        if path[-1] == "/":
            raise ValueError("Path is not valid as it ends with a trailing slash. (%s)" % (path))
        value_path = ""
        parent_value_path = ""
        for (predicate, _, path) in Utils.DROP_PREDICATES.findall(path):
            parent_value_path = value_path
            if value_path == "":
                value_path += "/" + module + ":" + path
                if not predicate == "":
                    raise NotImplementedError("The path %s is not handled by convert_path_to_value_path." % (value_path))
            else:
                value_path += predicate + "/" + path

        return value_path, parent_value_path

    @staticmethod
    def get_logger(name, level=logging.DEBUG):
        format = "%(asctime)-15s - %(name)-15s %(levelname)-12s  %(message)s"
        logging.basicConfig(level=99, format=format)
        log = logging.getLogger(name)
        log.setLevel(level)

        logging.addLevelName(7, "TRACE")
        logging.addLevelName(4, "CRAZY")

        def crazy(self, message, *args, **kws):
            if self.isEnabledFor(4):
                self._log(4, message, args, **kws)
        logging.Logger.crazy = crazy

        def trace(self, message, *args, **kws):
            if self.isEnabledFor(7):
                self._log(7, message, args, **kws)
        logging.Logger.trace = trace
        return log

    @staticmethod
    def get_yang_type_from_path(context, schema_path,  value, child_attr=None):
        if child_attr:
            schema_path = schema_path + "/" + context.module + ":" + child_attr
        node_schema = next(context.schemactx.find_path(schema_path))
        return Utils.get_yang_type(node_schema.type(), value, schema_path)

    def get_yang_type(node_schema, value=None, xpath=None, default_to_string=False):
        """
        Map a given yang-type (e.g. string, decimal64) to a type code for the backend.

        Sysrepo has a few cases- centered around the sr.Val() class
         1) For most types we can provide just the value
         2) For enumerations we must provide sr.SR_ENUM_T
         3) For uint32 (and other uints) we need to provide the type still (we can form the Val object without, but
            sysrepo will not accept the data)
         4) For decimal64 we must not provide any type
         5) As long as a uint8/16/32/64 int8/16/32/64 fits the range constraints sysrepo doesn't strictly enforce it
            (when considering a union of all 8 types). For simple leaves sysrepo is strict.

        Libyang gives us the following type from
          node = next(yangctx.find_path(`'/integrationtest:morecomplex/integrationtest:inner/integrationtest:leaf666'`))
          node.type().base()


        Unless we find a Union (11) or leafref (9) then we can just map directly.
        """

        base_type = node_schema.base()
        if base_type in Types.LIBYANG_MAPPING:
            return Types.LIBYANG_MAPPING[base_type]

        if base_type == 9:  # LEAF REF
            base_type = node_schema.leafref_type().base()
            node_schema = node_schema.leafref_type()
            if base_type in Types.LIBYANG_MAPPING:
                return Types.LIBYANG_MAPPING[base_type]

        if base_type == 11:  # Uninon
            """
            Note: for sysrepo if we are a union of enumerations and other types
            then we must set the data as sr.SR_ENUM_T if it matches the enumeration.
            e.g. leaf666/type6
            """

            u_types = []
            for union_type in node_schema.union_types():
                if union_type.base() == 11:
                    raise NotImplementedError('Union containing unions not supported (see README.md)')
                elif union_type.base() == 9:
                    raise NotImplementedError('Union containing leafrefs not supported (see README.md)')
                elif union_type.base() == 6:
                    # TODO: we need to lookup enumerations
                    for (val, validx) in union_type.enums():
                        if str(val) == str(value):
                            return Types.DATA_ABSTRACTION_MAPPING['ENUM']
                u_types.append(union_type.base())

            if 10 in u_types and isinstance(value, str):
                return Types.DATA_ABSTRACTION_MAPPING['STRING']
            elif isinstance(value, float):
                return Types.DATA_ABSTRACTION_MAPPING['DECIMAL64']
            if isinstance(value, int):
                return Utils._find_best_number_type(u_types, value)
        if default_to_string:
            return Types.DATA_ABSTRACTION_MAPPING['STRING']

        if value:
            msg = "Unable to match the value '%s' to a yang type for path %s - check the value." % (value, str(xpath))
            raise Errors.ValueNotMappedToType(xpath, value)

        msg = 'Unable to handle the yang type at path ' + str(xpath)
        msg += ' (this may be listed as a corner-case on the README already'
        raise NotImplementedError(msg)

    @staticmethod
    def _find_best_number_type(u_types, value):
        if 12 in u_types and value >= -127 and value <= 128:
            return Types.DATA_ABSTRACTION_MAPPING['INT8']
        elif 13 in u_types and value >= 0 and value <= 255:
            return Types.DATA_ABSTRACTION_MAPPING['UINT8']
        elif 14 in u_types and value >= -32768 and value <= 32767:
            return Types.DATA_ABSTRACTION_MAPPING['INT16']
        elif 15 in u_types and value >= 0 and value <= 65535:
            return Types.DATA_ABSTRACTION_MAPPING['UINT16']
        elif 16 in u_types and value >= -2147483648 and value <= 2147483647:
            return Types.DATA_ABSTRACTION_MAPPING['INT32']
        elif 17 in u_types and value >= 0 and value <= 4294967295:
            return Types.DATA_ABSTRACTION_MAPPING['UINT32']
        elif 19 in u_types and value >= 0:
            return Types.DATA_ABSTRACTION_MAPPING['UINT64']
        else:
            return Types.DATA_ABSTRACTION_MAPPING['INT64']

    @staticmethod
    def encode_xpath_predicate(k, v):
        """
        TODO: xpath predciates need some kind of encoding/escaping to make them safe (or complain
        they are not.
        example - [x='X'X'] is not safe.
        """
        return "[%s='%s']" % (k, v)

    @staticmethod
    def encode_xpath_predicates(attr, keys, values):
        """
        This method takes a list of keys and a list of value/value-type tuples)
        """
        if not isinstance(keys, list):
            raise NotImplementedError("encode_attribute_with_xpath_predicates does not work with non-list input - %s" % (keys))
        if not isinstance(values, list):
            raise NotImplementedError("encode_attribute_with_xpath_predicates does not work with non-list input - %s" % (values))
        answer = attr

        for i in range(len(keys)):
            (val, valtype) = values[i]
            answer = answer + Utils.encode_xpath_predicate(keys[i], Utils.get_xpath_value_from_python_value(val, valtype))
        return answer

    @staticmethod
    def get_xpath_value_from_python_value(v, t):
        if t == Types.DATA_ABSTRACTION_MAPPING['BOOLEAN']:
            return str(v).lower()
        else:
            return str(v)

    @classmethod
    def decode_xpath_predicate(self, path):
        """
        TODO: xpath predciates need some kind of encoding/escaping to make them safe (or complain
        they are not.
        example - [x='X'X'] is not safe.
        """

        results = self.LAST_LEAF_AND_PREDICTAES.findall(path)
        if not len(results) == 1:
            raise Errors.XpathDecodingError(path)

        (list_element_path_a, list_element_path_b, last_set_of_predicates) = results[0]

        predicates = {}
        for (key, val) in self.PREDICATE_KEY_VALUES_SINGLE.findall(path):
            predicates[key] = val
        for (key, val) in self.PREDICATE_KEY_VALUES_DOUBLE.findall(path):
            predicates[key] = val

        keys = []
        values = []
        for key in self.FIND_KEYS.findall(last_set_of_predicates):
            keys.append(key)
            values.append(predicates[key])

        return (list_element_path_a + list_element_path_b, tuple(keys), tuple(values))

    @staticmethod
    def convert_string_to_python_val(value, valtype):
        """
        Give a value and a value type convert it to a python representation instead of a string from the XML
        template.

        The valtype should correspond to yangvoodoo.Types.DATA_ABSTRACTION_MAPPING.
        """
        if valtype in Types.INT_CONVERSION:
            return int(value)
        elif valtype == Types.DATA_ABSTRACTION_MAPPING['DECIMAL64']:
            return float(value)
        elif valtype == Types.DATA_ABSTRACTION_MAPPING['BOOLEAN']:
            if value.toLower() == 'false':
                return False
            return True
        return value

    @staticmethod
    def get_nodeschema_from_data_path(context, path):
        """
        Given a properly formed data path return a corresponding schema node.
        """
        (schema_path, _) = Utils.convert_path_to_schema_path(path, context.module)

        try:
            node_schema = next(context.schemactx.find_path(schema_path))
        except libyang.util.LibyangError:
            raise Errors.NonExistingNode(schema_path)

        node_schema.real_schema_path = schema_path
        node_schema.real_data_path = path

        return node_schema

    @staticmethod
    def get_yangnode(node, context, attr='', keys=[], values=[], predicates=""):
        """
        Given a node, with a child attribute name, and list of key/values return a libyang schema object
        and the value path.

        Each time we return a node we will store the following on the yang node to help with underscore
        translations. The input to this method will have hyphens converted to underscores.
        - real_schema_path
        - real_data_path

        Libyang itself has schema_path and data_path but these do not know about the underscore translations.

        Remember:
         - schemapaths must have the yang module at every component
         - values paths only require the yang module prefix at the first component.
        The cache entries are built deliberately not to be a valid path (designated by the %).
        This is done so that we can lookup the cache without having to carry out processing.
        """

        if len(keys) and len(values):
            predicates = Utils.encode_xpath_predicates('', keys, values)

        cache_entry = "!" + node.real_data_path + attr + "!" + predicates + "!" + node.real_schema_path

        if context.schemacache.is_path_cached(cache_entry):
            return context.schemacache.get_item_from_cache(cache_entry)

        real_schema_path = node.real_schema_path
        if not attr == '':
            real_attribute_name = Utils.get_original_name(real_schema_path, context, attr)
            real_schema_path = real_schema_path + '/' + context.module + ":" + real_attribute_name

        try:
            node_schema = next(context.schemactx.find_path(real_schema_path))
        except libyang.util.LibyangError:
            raise Errors.NonExistingNode(node.real_schema_path + '/'+context.module+":"+attr)

        if not attr == '':
            real_data_path = node.real_data_path
            if node_schema.nodetype() not in (Types.LIBYANG_NODETYPE['CHOICE'], Types.LIBYANG_NODETYPE['CASE']):
                if node.real_data_path == '':
                    real_data_path = '/' + context.module + ':' + real_attribute_name + predicates
                else:
                    real_data_path = real_data_path + '/' + real_attribute_name + predicates

        if not attr:
            real_data_path = node.real_data_path + predicates
            real_schema_path = node.real_schema_path
            node_schema = node

        item = YangNode(node_schema, real_schema_path, real_data_path, node.real_data_path)

        context.schemacache.add_entry(cache_entry, item)

        return item

    @staticmethod
    def get_original_name(schema_path, context, attr):
        """
        Given a schema-path return the original name.
        """
        if '_' not in attr:
            return attr

        if schema_path == "":
            schema_path = "/" + context.module + ":*/*"
        else:
            schema_path = schema_path + "/*"
        for child in context.schemactx.find_path(schema_path):
            if child.name().replace('-', '_') == attr:
                return child.name()

        raise NotImplementedError("get_original_name could not find a matching node name for %s" % (attr))

    @staticmethod
    def get_keys_from_a_node(node_schema):
        keys = []
        for k in node_schema.keys():
            keys.append(k.name())
        return keys

    @staticmethod
    def convert_args_to_list(node, *args):
        if isinstance(args[0], tuple):
            return list(args[0])
        return list(args)

    @staticmethod
    def get_key_val_tuples(context, node,  values):
        real_values = []
        keys = Utils.get_keys_from_a_node(node)

        i = 0
        if isinstance(values[0], tuple):
            values = values[0]

        if not len(keys) == len(values):
            raise Errors.ListWrongNumberOfKeys(node.real_data_path, len(keys), len(values))
        for value in values:
            key_yang_type = Utils.get_yang_type_from_path(context, node.real_schema_path, value, keys[i])
            real_values.append((value, key_yang_type))

        return keys, real_values

    @staticmethod
    def best_guess_of_yang_type(node_schema_type, child_text, this_path):
        """
        TODO: still want to create a proper validator class to properly recurse through union/typedef/leafrefs
        and find the best match. This will do for now.

        This is currently used by TemplateNinja
        """
        try:
            return Utils.get_yang_type(node_schema_type, child_text, this_path)
        except Errors.ValueNotMappedToType:
            pass

        return Utils.get_yang_type(node_schema_type, int(child_text), this_path)

    @staticmethod
    def _handle_portion_of_xpath(portion, answer, inside_a_predicate):
        raise ValueError("This should be possible tremove")

        """
        Handle a portion of xpath , based on a primitive split by '/',
        giving back to the value anything which as a '/' in it.
        """
        if inside_a_predicate:
            answer[-1] += "/" + portion
            if Utils.ENDING_A_PREDICATE.match(portion):
                return False
            return True
        answer.append(portion)
        if Utils.STARTING_A_PREDICATE.match(portion):
            if Utils.ENDING_A_PREDICATE.match(portion):
                return False
            return True

        return False

    @staticmethod
    def convert_xpath_to_list_v4(xpath):
        """
        Return a list of tuples based upon the XPATH sent in.
                (path, predicates, schema path, parent path)

        """
        module = "integrationtest"
        working_schema_path = ""
        working_path = ""
        parent_path = ""

        for (a, b, leaf_name, predicates, e, f) in Utils.XPATH_DECODER_V4.findall(xpath):
            parent_path = working_path
            working_path = working_path + "/" + leaf_name + predicates
            working_schema_path = working_schema_path + "/" + module + ":"+leaf_name
            yield (working_path, leaf_name, predicates, working_schema_path, parent_path)

    @staticmethod
    def return_module_name_and_leaf(in_string):
        (module, node) = Utils.MODULE_AND_LEAF_REGEX.match(in_string).groups()
        if module:
            return (module[:-1], node)
        return (module, node)

    @staticmethod
    def return_until_first_predicate(in_string):
        return in_string[0:in_string.find('[')]

    @staticmethod
    def drop_last_node(in_string):
        return in_string[0:in_string.rfind('/')]

    @staticmethod
    def get_last_node_name(in_string):
        return in_string[in_string.rfind('/')+1:]

    @staticmethod
    def drop_module_name_from_xpath(in_string, module):
        if in_string[0:len(module)+2] == "/"+module+":":
            return "/" + in_string[len(module)+2:]
        return in_string

    @staticmethod
    def return_except_last_predicates(in_string):
        """ Assuming well formed xpaths with [] not valid in keys. """
        # return in_string[in_string.rfind(']'):]
        return Utils.XPATH_MATCH_AFTER_LAST_PREDICATE.sub(r'\g<1>', in_string)

    @staticmethod
    def drop_all_predicates(in_string):
        return Utils.DROP_ALL_PREDICATES.sub('', in_string)
