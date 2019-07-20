from yangvoodoo.Common import Utils
from yangvoodoo.Errors import UnableToLockDatastoreError, LockWasBrokenDuringTransactionError
import yangvoodoo.basedal
import redis
import time
import uuid


class RedisDataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):

    """
    This module provides the redis abstraction layer.

    Read-operations will be taken straight to REDIS, there is no caching involved,
    nothing stops this data_abstraction_layer being combined with the proxydal
    class.

    Write-opterations will be held back.

    To experiment with Redis:  docker run -p 6379:6379 -i -t redis

    There is more complexity in this dal to give a shim of transactionality over
    the top of redis.
    """

    DAL_ID = "RedisDal"

    def __init__(self, log=None):
        if not log:
            log = Utils.get_logger(self.DAL_ID)
        self.log = log
        self.session = None
        self.conn = None
        self.dirty = None
        self.datastore_changed = None
        self.module = None
        self.redis = None
        self.id = str(uuid.uuid4())

        self._initdal()

    def _initdal(self):
        self.log.info("REDIS ID: %s", self.id)
        self.refresh()

    def refresh(self):
        self.paths_removed = {}
        self.paths_set = {}

    def connect(self, tag='client'):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)

    def disconnect(self):
        raise NotImplementedError('disconnect not implemented')

    def _get_lock(self, wait=50, interval=0.1):
        self.log.trace("Attempting to get a lock to redis %s * %s", wait, interval)
        for c in range(wait):
            if self.redis.setnx("/internal/transaction-lock", self.id):
                lock = self.redis.get("/internal/transaction-lock")
                self.log.trace("Obtained Lock: %s", lock)
                return True

        lock_owner = self.redis.get("/internal/transaction-lock")
        raise UnableToLockDatastoreError(lock_owner)

    def _release_lock(self):
        self.log.trace("Releasing lock")
        lock_owner = self.redis.get("/internal/transaction-lock").decode('utf-8')
        if lock_owner == self.id:
            self.redis.delete("/internal/transaction-lock")
            return True
        raise LockWasBrokenDuringTransactionError(lock_owner)

    def commit(self):
        self.log.trace("COMMIT: to delete: %s to set:%s", len(self.paths_removed), len(self.paths_set))
        self._get_lock()
        try:
            for path in self.paths_set:
                self.redis.set(path, self.paths_set[path])
            self.paths_set = {}
        except Exception:
            pass
        finally:
            self._release_lock()

        return True

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
        raise NotImplementedError("create not implemented")

    def uncreate(self, xpath):
        """
        To remove a list item from the list /simplelist with the key sf

        xpath:   /integrationtest:simplelist[simplekey='sf']
        """
        raise NotImplementedError("uncreate not implemented")

    def set(self, xpath, value, valtype=18):
        self.log.trace("SET: %s => %s (valtype: %s)", xpath, value, valtype)
        self.paths_set[xpath] = value
        if xpath in self.paths_removed:
            del self.paths_removed[xpath]
        return True

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

    def has_item(self, xpath):
        """
        Check to see if the list-element of a YANG list exists.

        xpath:          /integrationtest:simplelist[simplekey='b']
        """
        raise NotImplementedError("has_item not implemented")

    def get(self, xpath, default_value=None):
        self.log.trace("GET: %s (default value: %s)", xpath, default_value)
        val = None
        if val not in self.paths_removed:
            val = self.redis.get(xpath)
            if val:
                return val.decode('utf-8')

        if val is None and xpath in self.paths_set:
            val = self.paths_set[xpath]

        if val is None and default_value:
            return default_value
        return val

    def delete(self, xpath):
        self.log.trace("DELETE: %s", xpath)
        self.paths_removed[xpath] = True
        return True

    def is_session_dirty(self):
        raise NotImplementedError("is_session_dirty not implemented")

    def has_datastore_changed(self):
        raise NotImplementedError("has_datastore_changed not implemented")

    def dump_xpaths(self):
        raise NotImplementedError("dump_xpaths not implemented")

    def empty(self):
        self.log.warning("EMPTY: called")
        self.redis.flushall()
