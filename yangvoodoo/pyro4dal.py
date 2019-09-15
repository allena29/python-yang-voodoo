import Pyro4
import yangvoodoo
from yangvoodoo.Common import Utils


class PyroDataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):

    """
    This module provides a pyro4 based remote access data abstraction layer.

    The user should take care of setting symmetric keys and control network access to the
    pyro4 processes in order to consider access security.

    Unlike other DAL's which offer vary levels of transactionality to their data, this
    deliberately does not have *ANY* transactionality at all. If there is a requirement
    for transactionality then this could be provided by coupling with a proxy layer. This
    means the following methods are not useful.
        - has_datastore_changed
        - is session_dirty
        - refresh
        - validate
        - commit

    The backend pyro4 daemon is responsible for deciding how and when to persist data
    to disk.
    """

    DAL_ID = 'PYRO4'

    def pyro4_connect(self, hostname, nameserver, hmac_key='this-value-is-a-dummy-hmac-key'):
        object_id = 'net.mellon-collie.yangvooodoo.pyro4bridge.' + hostname
        self.log.info('Connecting to pyro4 %s via %s', object_id, nameserver)

        ns = Pyro4.locateNS(nameserver)
        uri = ns.lookup(object_id)

        self.pyro_obj = Pyro4.Proxy(uri)
        self.pyro_obj._pyroHmacKey = hmac_key
        self.log.debug('URI: %s', self.pyro_obj)

    def _initdal(self):
        """
        Initialise specific class attributes for a particular dal.
        """
        self.pyro4 = None

    def disconnect(self):
        pass

    def commit(self):
        self.log.warning('Commit has not effect on PyroDAL')

    def validate(self):
        self.log.warning('Validate has not effect on PyroDAL')

    def container(self, xpath):
        """
        Returns if the presence container exists or not.

        xpath:     /integrationtest:simplecontainer
        """
        return self.pyro_obj.container(xpath)

    def create_container(self, xpath):
        """
        To create a presence container.

        xpath:     /integrationtest:simplecontainer
        """
        return self.pyro_obj.create_container(xpath)

    def create(self, xpath, keys=None, values=None, module=None):
        """
        To create a list item in the list /simplelist

        xpath:    /integrationtest:simplelist[simplekey='sdf']
        keys:     ('simplekey',),
                    tuple of keys in the order defined within yang.
        values:   [('simpleval', 18)],
                    list of (value, valtype) tuples

        module:   integrationtest

        Returns a generator providing a list of XPATH values for each ListElement
            "/integrationtest:simplelist[simplekey='simpleval']",
            "/integrationtest:simplelist[simplekey='zsimpleval']",
            "/integrationtest:simplelist[simplekey='asimpleval']"

        If there are multiple keys the predicates are combined (e.g.)
            /integration:list[key1='val1'][key2='val2']
        """
        return self.pyro_obj.create(xpath, keys, values, module)

    def uncreate(self, xpath):
        """
        To remove a list item from the list /simplelist with the key sf

        xpath:   /integrationtest:simplelist[simplekey='sf']
        """
        return self.pyro_obj.uncreate(xpath)

    def set(self, xpath, value, valtype=18, nodetype=4):
        return self.pyro_obj.set(xpath, value, valtype, nodetype)

    def gets(self, xpath):
        return self.pyro_obj.gets(xpath)

    def gets_len(self, xpath):
        """
        From a given XPATH list (not leaf-list) return the legnth of the list.

        xpath:       /integrationtest:web/bands[name='Idlewild']/gigs
        """
        return self.pyro_obj.gets_len(xpath)

    def add(self, xpath, value, valtype=10):
        """
        To create a leaf-list item in /morecomplex/leaflists/simple

        xpath:       /integrationtest:morecomplex/integrationtest:leaflists/integrationtest:simple
        value:       a
        valtype:     18
        """
        return self.pyro_obj.add(xpath, value, valtype)

    def remove(self, xpath, value):
        return self.pyro_obj.remove(xpath, value)

    def gets_unsorted(self, xpath, schema_path, ignore_empty_lists=False):
        """
        To retrieve a list of XPATH's as a generator to each list element in the list.
        The order remains in the order the user added items to the list.

        xpath:       /integrationtest:web/bands[name='Idlewild']/gigs
        schema_path: /integrationtest:web/integrationtest:bands/integrationtest:gigs

        returns a generator.
        """
        return self.pyro_obj.gets_unsorted(xpath, schema_path, ignore_empty_lists=False)

    def has_item(self, xpath):
        """
        Check to see if the list-element of a YANG list exists.

        xpath:          /integrationtest:simplelist[simplekey='b']
        """
        return self.pyro_obj.has_item(xpath)

    def get(self, xpath, default_value=None):
        val = self.pyro_obj.get(xpath, default_value)
        if not val and default_value:
            return default_value
        return val

    def delete(self, xpath):
        raise NotImplementedError("delete not implemented")

    def refresh(self):
        self.log.warning('refresh has no effect for pyro dal')

    def is_session_dirty(self):
        self.log.warning('is session dirty has no effect for pyro dal')

    def has_datastore_changed(self):
        self.log.warning('has data_store_changed has no effect for pyro dal')

    def dump_xpaths(self):
        raise NotImplementedError("dump_xpaths not implemented")

    def empty(self):
        raise NotImplementedError("empty not implemented")

    def dump(self, filename, format=1):
        raise NotImplementedError("export not implemented")

    def load(self, filename, format=1):
        raise NotImplementedError("import not implemented")

    def dumps(self, format=1):
        return self.pyro_obj.dumps(format)

    def loads(self, payload, format=1):
        raise NotImplementedError("import not implemented")
