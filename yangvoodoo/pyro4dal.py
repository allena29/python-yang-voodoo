import yangvoodoo
import yangvoodoo.basedal
import Pyro4


class Pyro4DataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):

    """
    EXPERIMENTAL PYRO4 BASED DATA ABSTRACTION LAYER.

    The idea here is to help create a lighter way means of using interacting with
    a datastore.

    A corresponding backend daemon must be prvided to bridge to the datastore.

    The basic pyro4 daemon can look something like this
    import Pyro4


    @Pyro4.expose
    class GreetingMaker(object):
        def get_fortune(self, name):
            print(Pyro4.current_context.client_sock_addr)
            return "Hello, {0}. Here is your fortune message:\n" \
                   "Tomorrow's lucky number is 12345678.".format(name)


    daemon = Pyro4.Daemon(host='192.168.3.1')                # make a Pyro daemon
    ns = Pyro4.locateNS()                  # find the name server
    uri = daemon.register(GreetingMaker)   # register the greeting maker as a Pyro object
    ns.register("example.greeting", uri)   # register the object with a name in the name server

    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls


    """

    DAL_ID = "Pyro4DAL"
    DAL_IN_MEMORY = False

    def _get_pyro4_nameserver(self):
        return Pyro4.locateNS

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
        """
        Connect to the backend pyro4 object bridge.
        """
        self.module = module

        ns = self._get_pyro4_nameserver()
        uri = ns.lookup("yangvooodoo.mellon-collie.net.yangvoodoo.dal.backend.bridge")
        self.conn = Pyro4.Proxy(uri)

        return True

    def disconnect(self):
        self.conn = None
        return True

    def commit(self):
        if not self.dirty:
            raise yangvoodoo.Errors.NothingToCommit()

        if not self.conn:
            raise yangvoodoo.Errors.NotConnect()

        self.conn.commit()

        self.dirty = False
        return True

    def validate(self):
        if not self.conn:
            raise yangvoodoo.Errors.NotConnect()

        self.conn.validate()

        return True

    def container(self, xpath):
        return xpath in self.containers

    def create_container(self, xpath):
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

    def create(self, xpath, keys=[], values=[]):
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
        self.dirty = True
        predicates = ""
        for index in range(len(keys)):
            (value, valuetype) = values[index]
            predicates = predicates + "["+keys[index]+"='"+str(value)+"']"

        list_xpath = xpath.replace(predicates, '')
        if list_xpath not in self.list_element_map:
            self.list_element_map[list_xpath] = []
        self.list_element_map[list_xpath].append(xpath)
        self.stub_store[xpath] = (self.LIST_POINTER, list_xpath)

        for index in range(len(keys)):
            (value, valuetype) = values[index]
            self.set(xpath + "/" + keys[index], value, valuetype)

    def uncreate(self, xpath):
        self.dirty = True
        self.delete(xpath)

    def add(self, xpath, value, valtype):
        self.dirty = True
        if xpath not in self.stub_store:
            self.stub_store[xpath] = []
        if value not in self.stub_store[xpath]:
            self.stub_store[xpath].append(value)

    def remove(self, xpath, value):
        self.dirty = True
        if xpath not in self.stub_store:
            raise yangvoodoo.Errors.BackendDatastoreError([('path does not exist - cannot remove', xpath)])
        if value not in self.stub_store[xpath]:
            raise yangvoodoo.Errors.BackendDatastoreError([('values does not exist at path - cannot remove', xpath)])
        self.stub_store[xpath].remove(value)

    def gets(self, xpath):
        items = []
        if xpath in self.stub_store:
            items = self.stub_store[xpath]
        for item in items:
            yield item

    def has_item(self, xpath):
        list_xpath = self._list_xpath(xpath, ignore_empty_lists=True)
        if list_xpath in self.list_element_map:
            if xpath in self.list_element_map[list_xpath]:
                return True
        return False

    def set(self, xpath, value, valtype=0):
        # if an empty Node stub will store this as True (sysrepo will not want a value)
        if valtype == 5:
            value = True
        self.dirty = True
        self.stub_store[xpath] = value

    def gets_sorted(self, list_xpath, schema_path, ignore_empty_lists=False):
        if list_xpath in self.list_element_map:
            items = []
            for item in self.list_element_map[list_xpath]:
                items.append(item)
            items.sort()
            for item in items:
                yield item

    def gets_unsorted(self, list_xpath, schema_path, ignore_empty_lists=False):
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
        if list_xpath in self.list_element_map:
            return len(self.list_element_map[list_xpath])
        return 0

    def get(self, xpath, default_value=None):
        if xpath not in self.stub_store:
            if default_value:
                return default_value
            return None
        return self.stub_store[xpath]

    def delete(self, xpath):
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
        self.dirty = False
        pass

    def empty(self):
        self.stub_store = {}
        self.list_element_map = {}
        self.containers = {}

    def is_session_dirty(self):
        return self.dirty

    def has_datastore_changed(self):
        return False
