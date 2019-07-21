import yangvoodoo
import yangvoodoo.basedal


class StubDataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):

    """
    IMPORTANT:

    This data abstration layer is a stub which is not suitable for any real use case - it's sole
    purpose is to allow for testing without the dependency of running the sysrepo backend.

    In general this means that whilst manipulating the data as part of yangvoodoo node it is
    only a candidate transaction. The follow up committing the data allows the backend datastore
    to have the final say on it's validity

    There are some key constraints:


    1) VoodooNode utilises libyang to lookup the schema of a given yang model - this enforces the
       overall schema.
        (i.e. root.<non-existatnt-node   <-- node must exist in the yang model).
              root.<boolean-node>        <-- assigning a non-boolean value fails.)

    2) Default values are provided by the backend datastore.

    3) Validating expressions from MUST and WHEN's is implemented by the backend datastore.


    """

    LIST_POINTER = 1
    DAL_ID = "StubDAL"
    DAL_IN_MEMORY = True

    def dump_xpaths(self):
        new_dict = {}
        for key in self.stub_store:
            if isinstance(self.stub_store[key], tuple):
                pass
                # new_dict[key] = self.stub_store[key][1]
            else:
                new_dict[key] = self.stub_store[key]
        return new_dict

    def _initdal(self):
        self.empty()

    def connect(self, module, tag='<id-tag>'):
        self.log.trace('CONNECT: Stub Datastore- module name %s', module)
        self.module = module
        return True

    def disconnect(self):
        self.log.trace('DISCONNET')
        return True

    def commit(self):
        self.log.trace('COMMIT')
        if not self.dirty:
            raise yangvoodoo.Errors.NothingToCommit()

        self.dirty = False
        return True

    def validate(self):
        self.log.trace('VALIDATE')
        return True

    def container(self, xpath):
        self.log.trace('CONTAINER (does it exist?): %s', xpath)
        return xpath in self.containers

    def create_container(self, xpath):
        self.log.trace('CREATE-CONTAINER: %s', xpath)
        self.dirty = True
        self.containers[xpath] = True

    def _list_xpath(self, xpath, ignore_empty_lists=False):
        """
        Convert a list operation into a path without the last set of predictes

        This is specific to the way we organise lists in the stub node.
        """
        if xpath not in self.stub_store:
            if ignore_empty_lists:
                return None
            raise ValueError('Path does not exist %s' % (xpath))
        (itemtype, item) = self.stub_store[xpath]
        if not itemtype == self.LIST_POINTER:
            if ignore_empty_lists:
                return None
            raise ValueError('Path is not a list %s' % (xpath))

        return item

    def create(self, xpath, keys=[], values=[], list_xpath=None):
        """
        The xpath coming in should include the full predicates
            /integrationtest:simplelist[integrationtest:simplekey='sdf']

        However in the stub to speed up iteration we create a structure
            self.stub_store[xpath_without_predicates]

        In the stub we create a python list, this holds precise XPATH's to each list element
            /integrationtest:simplelist = []
        The keys/values are used to create, this is a specific list element for each key and matches sysrepo
            /integrationtest:simplelist[integrationtest:simplekey='sdf']/integrationtest:<key0> = <value0>

        We also create the following keys- pointing back the list without any predicates
            "/integrationtest:simplelist[integrationtest:simplekey='sdf']": = (1, "list path")

        """

        self.log.trace('CREATE-LIST-ELEMENT: %s (keys: %s, values: %s)', xpath, keys, values)
        self.dirty = True

        if list_xpath not in self.list_element_map:
            self.list_element_map[list_xpath] = []
        self.list_element_map[list_xpath].append(xpath)
        self.stub_store[xpath] = (self.LIST_POINTER, list_xpath)

        for index in range(len(keys)):
            (value, valuetype) = values[index]
            self.set(xpath + "/" + keys[index], value, valuetype)

    def uncreate(self, xpath, list_xpath=None):
        self.log.trace('UNCREATE-LIST-ELEMENT: %s', xpath)
        self.dirty = True
        self.delete(xpath)

    def add(self, xpath, value, valtype):
        self.log.trace('ADD-LEAF-LIST: %s => %s (%s)', xpath, value, valtype)
        self.dirty = True
        if xpath not in self.stub_store:
            self.stub_store[xpath] = []
        if value not in self.stub_store[xpath]:
            self.stub_store[xpath].append(value)

    def remove(self, xpath, value):
        self.log.trace('REMOVE-LEAF-LIST: %s => %s', xpath, value)
        self.dirty = True
        if xpath not in self.stub_store:
            raise yangvoodoo.Errors.BackendDatastoreError([('path does not exist - cannot remove', xpath)])
        if value not in self.stub_store[xpath]:
            raise yangvoodoo.Errors.BackendDatastoreError([('values does not exist at path - cannot remove', xpath)])
        self.stub_store[xpath].remove(value)

    def gets(self, xpath):
        self.log.trace('GETS: %s', xpath)
        items = []
        if xpath in self.stub_store:
            items = self.stub_store[xpath]
        for item in items:
            yield item

    def has_item(self, xpath, list_xpath):
        self.log.trace('HAS_ITEM: %s', xpath)
        if list_xpath in self.list_element_map:
            if xpath in self.list_element_map[list_xpath]:
                return True
        return False

    def set(self, xpath, value, valtype=0):
        self.log.trace("SET: %s => %s (%s)", xpath, value, valtype)
        # if an empty Node stub will store this as True (sysrepo will not want a value)
        if valtype == 5:
            value = True
        self.dirty = True
        self.stub_store[xpath] = value

    def gets_sorted(self, list_xpath, schema_path, ignore_empty_lists=False):
        self.log.trace("GETS_SORTED: %s . %s", list_xpath, schema_path)
        if list_xpath in self.list_element_map:
            items = []
            for item in self.list_element_map[list_xpath]:
                items.append(item)
            items.sort()
            for item in items:
                yield item

    def gets_unsorted(self, list_xpath, schema_path, ignore_empty_lists=False):
        self.log.trace("GETS_UNSORTED: %s . %s", list_xpath, schema_path)
        if list_xpath in self.list_element_map:
            items = []
            for item in self.list_element_map[list_xpath]:
                items.append(item)
            for item in items:
                yield item
            return
        if not ignore_empty_lists:
            raise yangvoodoo.Errors.ListDoesNotContainElement(list_xpath)

    def gets_len(self, list_xpath):
        self.log.trace("GETS_LEN: %s", list_xpath)
        if list_xpath in self.list_element_map:
            return len(self.list_element_map[list_xpath])
        return 0

    def get(self, xpath, default_value=None):
        self.log.trace("GET: %s (default value: %s)", xpath, default_value)
        if xpath not in self.stub_store:
            if default_value:
                return default_value
            return None
        return self.stub_store[xpath]

    def delete(self, xpath):
        self.log.trace("DELETE: %s", xpath)
        self.dirty = True
        if xpath in self.stub_store:
            # Logic for lists
            if xpath[-1] == "]":
                list_xpath = self._list_xpath(xpath)
                if list_xpath not in self.list_element_map:
                    raise yangvoodoo.Errors.BackendDatastoreError([('path does not exist - cannot get', xpath)])
                elif xpath not in self.list_element_map[list_xpath]:
                    raise yangvoodoo.Errors.BackendDatastoreError([('path does not exist - cannot get', xpath)])
                else:
                    self.list_element_map[list_xpath].remove(xpath)
                    del self.stub_store[xpath]
                    self._delete_childern(xpath)
                    return True

            del self.stub_store[xpath]
        self._delete_childern(xpath)
        return True

    def _delete_childern(self, xpath):
        children_to_remove = []
        for x in self.stub_store.keys():
            if x[0:len(xpath)] == xpath:
                if x not in children_to_remove:
                    children_to_remove.append(x)

        for child in children_to_remove:
            del self.stub_store[child]

    def refresh(self):
        self.log.trace("REFRESH:")
        self.dirty = False
        pass

    def empty(self):
        self.log.trace("EMPTY:")
        self.stub_store = {}
        self.list_element_map = {}
        self.containers = {}

    def is_session_dirty(self):
        self.log.trace("IS_SESSION_DIRTY")
        return self.dirty

    def has_datastore_changed(self):
        self.log.trace("HAS_DATASTORE_CHANGED")
        return False
