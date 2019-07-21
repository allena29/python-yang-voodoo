from yangvoodoo.Common import Utils


class BaseDataAbstractionLayer:

    """
    This module provides the base definition of the data abstraction layer.

    Log         - a standard python logger
    session     - represents the session to the data access layer
    conn        - represents the socket/connection uses to access the data access layer.
    dirty       - indicates a parallel transaction has changed data in the datastore.
    module      - the name of the YANG module implemented by this session. Note: there is
                  a 1:1 mapping between sessions and yang modules.

    Value Types:
        values are a tuple of the exact value and the type.
        see Types.DATA_ABSTRACTION_MAPPING for the definition of types.

    """

    DAL_ID = "BASE"

    def __init__(self, log=None):
        if not log:
            log = Utils.get_logger(self.DAL_ID)
        self.log = log
        self.session = None
        self.conn = None
        self.dirty = None
        self.datastore_changed = None
        self.module = None
        self._initdal()

    def _initdal(self):
        """
        Initialise specific class attributes for a particular dal.
        """
        pass

    def setup_root(self):
        """
        If required may be used to carry out to do any preparation before a root object
        is obtained.
        """
        pass

    def load_xpaths(self, xpaths):
        """
        Given a dictionary of XPATH's import them to the datastore.

        xpath[key] = (value, valuetype, nodetype)

        valuetype  - see Types.DATA_ABSTRACTION_MAPPING
        nodetype   - see Types.LIBYANG_NODETYPE
        """
        for xpath in xpaths:
            (value, valuetype, nodetype) = xpaths[xpath]
            if isinstance(value, list):
                for (value, valuetype, nodetype) in xpaths[xpath]:
                    print('INNIN Leaf list add required', xpath)
                    self.add(xpath, value, valuetype)
            else:
                print('INNIN', xpath, nodetype)
                (value, valuetype, nodetype) = xpaths[xpath]
                if nodetype == 16:  # list

                    self.create(xpath)
                    print('INNIN - list create', xpath)
                elif value:
                    print('INNIN - value', xpath, value)
                    self.set(xpath, value, valuetype)

    def connect(self, tag='client'):
        raise NotImplementedError('connect not implemented')

    def disconnect(self):
        raise NotImplementedError('disconnect not implemented')

    def commit(self):
        raise NotImplementedError('commit not implemented')

    def validate(self):
        raise NotImplementedError('validate not implemented')

    def container(self, xpath):
        """
        Returns if the presence container exists or not.

        xpath:     /integrationtest:simplecontainer
        """
        raise NotImplementedError('container not implemented')

    def create_container(self, xpath):
        """
        To create a presence container.

        xpath:     /integrationtest:simplecontainer
        """
        raise NotImplementedError('create_container not implemented')

    def create(self, xpath, keys=None, values=None, module=None, list_xpath=None):
        """
        To create a list item in the list /simplelist

        xpath:    /integrationtest:simplelist[simplekey='sdf']
        keys:     ('simplekey',),
                    tuple of keys in the order defined within yang.
        values:   [('simpleval', 18)],
                    list of (value, valtype) tuples
        listxpath: /integrationtest:simplelist

        module:   integrationtest

        Returns a generator providing a list of XPATH values for each ListElement
            "/integrationtest:simplelist[simplekey='simpleval']",
            "/integrationtest:simplelist[simplekey='zsimpleval']",
            "/integrationtest:simplelist[simplekey='asimpleval']"

        If there are multiple keys the predicates are combined (e.g.)
            /integration:list[key1='val1'][key2='val2']
        """
        raise NotImplementedError("create not implemented")

    def uncreate(self, xpath, list_xpath=None):
        """
        To remove a list item from the list /simplelist with the key sf

        xpath:     /integrationtest:simplelist[simplekey='sf']
        listxpath: /integrationtest:simplelist
        """
        raise NotImplementedError("uncreate not implemented")

    def set(self, xpath, value, valtype=18):
        raise NotImplementedError("set not implemented")

    def gets_sorted(self, xpath, schema_path, ignore_empty_lists=False):
        """
        To retrieve a list of XPATH's as a generator to each list element in the list.
        The order is sorted by XPATH before getting returned.

        xpath:       /integrationtest:web/bands[name='Idlewild']/gigs
        schema_path: /integrationtest:web/integrationtest:bands/integrationtest:gigs

        returns a generator.
        """
        raise NotImplementedError("gets_sorted not implemented")

    def gets(self, xpath):
        raise NotImplementedError("gets not implemented")

    def gets_len(self, xpath):
        """
        From a given XPATH list (not leaf-list) return the legnth of the list.

        xpath:       /integrationtest:web/bands[name='Idlewild']/gigs
        """
        raise NotImplementedError("gets_len not implemented")

    def add(self, xpath, value, valtype=18):
        """
        To create a leaf-list item in /morecomplex/leaflists/simple

        xpath:       /integrationtest:morecomplex/integrationtest:leaflists/integrationtest:simple
        value:       a
        valtype:     18
        """
        raise NotImplementedError("add not implemented")

    def remove(self, xpath, value):
        raise NotImplementedError("remove not implemented")

    def gets_unsorted(self, xpath, schema_path, ignore_empty_lists=False):
        """
        To retrieve a list of XPATH's as a generator to each list element in the list.
        The order remains in the order the user added items to the list.

        xpath:       /integrationtest:web/bands[name='Idlewild']/gigs
        schema_path: /integrationtest:web/integrationtest:bands/integrationtest:gigs

        returns a generator.
        """
        raise NotImplementedError("gets_unsorted not implemented")

    def has_item(self, xpath, list_xpath):
        """
        Check to see if the list-element of a YANG list exists.

        xpath:          /integrationtest:simplelist[simplekey='b']
        """
        raise NotImplementedError("has_item not implemented")

    def get(self, xpath, default_value=None):
        raise NotImplementedError("get not implemented")

    def delete(self, xpath):
        raise NotImplementedError("delete not implemented")

    def refresh(self):
        raise NotImplementedError("refresh not implemented")

    def is_session_dirty(self):
        raise NotImplementedError("is_session_dirty not implemented")

    def has_datastore_changed(self):
        raise NotImplementedError("has_datastore_changed not implemented")

    def dump_xpaths(self):
        raise NotImplementedError("dump_xpaths not implemented")

    def empty(self):
        raise NotImplementedError("empty not implemented")
