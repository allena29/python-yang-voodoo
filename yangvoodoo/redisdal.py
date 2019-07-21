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

    The things we store are
     - data/<xpath> = value
     - metadata-listkey = a sorted set provide a list of xpaths for each list element

    There is more complexity in this dal to give a shim of transactionality over
    the top of redis. As write/delete options happen we store those in a set of
    dictionaries (set/get) these are then played-back to REDIS as part of the commit.

    An alternative approach to get in some transactionality is to set the data
    as data-<uuid>/ in real time. However we still have to track deletes, and
    we have to then copy the adds back in.


    Problems here:
    a) we don't have the type of nodes - suggestion is to expose a pyro4 service
       to give yang types.

       Pyro4 is potentially better than REDIS because we can return objects (potentially
       even a voodoo's YangNode representation)
        (although pyro4 has limitations on dunder's)

    b) The lack of transactionality is a pain - it's probably better just to go with the
       It's probably better to go with the stub node itself (proxy-less) and just implement
       validate/refresh in that object which goes out to redis. We have less work to do then
       with converting from binary encoded values

    c) dump_xpaths' needs some more specification, as it can only delete the things we know
       about.

       There are different approachs, do we want dump_xpath's to dump everything that has
       changed as part of the transaction so far (ignoring all other background data)
       or the entire data store.

       It's the former in the stub case today.
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
        self.paths_leaflist_set = {}
        self.paths_leaflist_removed = {}
        self.paths_list_set = {}
        self.paths_list_removed = {}

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
            time.sleep(interval)

        lock_owner = self.redis.get("/internal/transaction-lock")
        raise UnableToLockDatastoreError(lock_owner)

    def _release_lock(self):
        self.log.trace("Releasing lock")
        lock_owner = self.redis.get("/internal/transaction-lock").decode('utf-8')
        if lock_owner == self.id:
            self.redis.delete("/internal/transaction-lock")
            return True
        raise LockWasBrokenDuringTransactionError(lock_owner)

    def _set_leaves(self):
        self.log.trace("- Setting leaves")
        for path in self.paths_set:
            self.redis.set(path, self.paths_set[path])
        self.paths_set = {}

    def _remove_leaves(self):
        self.log.trace("- Removings leaves")
        for path in self.paths_removed:
            self.redis.delete(path)
        self.paths_removed = {}

    def _set_leaflists(self):
        self.log.trace(" - Setting leaf lists")
        for xpath in self.paths_leaflist_set:
            index = self.redis.zcount(xpath, '-inf', '+inf')
            for value in self.paths_leaflist_set[xpath]:
                self.redis.zadd(xpath, {value: index})
                index = index + 1
        self.paths_leaflist_set = {}

    def _remove_leaflists(self):
        self.log.trace(" - Remove leaf lists")
        for xpath in self.paths_leaflist_removed:
            for value in self.paths_leaflist_removed[xpath]:
                self.redis.zrem(xpath, value)
                # score = self.redis.zscore(xpath, value)
                # if score:
                #    self.redis.srem(xpath, value)
        self.paths_leaflist_removed = {}

    def _remove_lists(self):
        self.log.trace(" - Remove lists")
        for list_xpath in self.paths_list_removed:
            for xpath in self.paths_list_removed[list_xpath]:
                self.redis.zrem(list_xpath, xpath)
                self._remove_children(xpath)
                # score = self.redis.zscore(xpath, value)
                # if score:
                #    self.redis.srem(xpath, value)
        self.paths_list_removed = {}

    def _remove_children(self, xpath):
        xpath = xpath[xpath.find("/")+1:]
        self.log.trace(" - Remove children of %s", xpath)
        search = "data*/" + xpath.replace('[', '\\[').replace('*', '\\*') + "*"
        for key_to_delete in self.redis.keys(search):
            self.redis.delete(key_to_delete)

    def _set_lists(self):
        self.log.trace(" - Setting  lists")
        for list_xpath in self.paths_list_set:
            index = self.redis.zcount(list_xpath, '-inf', '+inf')
            for value in self.paths_list_set[list_xpath]:
                self.redis.zadd(list_xpath, {value: index})
                index = index + 1
        self.paths_list_set = {}

    def commit(self):
        self.log.trace("COMMIT: to delete: %s to set:%s", len(self.paths_removed), len(self.paths_set))
        self._get_lock()

        try:
            self._remove_leaves()
            self._set_leaves()
            self._remove_leaflists()
            self._set_leaflists()
            self._remove_lists()
            self._set_lists()
        except ImportError:
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
        xpath = "data" + xpath
        self.log.trace("CONTAINER: %s ", xpath)

        if xpath in self.paths_set:
            return True

        if self.redis.get(xpath):
            return True

        return False

    def create_container(self, xpath):
        """
        To create a presence container.

        xpath:     /integrationtest:simplecontainer
        """
        self.dirty = True
        xpath = "data" + xpath
        self.log.trace("CREATE-CONTAINER: %s ", xpath)
        self.paths_set[xpath] = '__container'
        # if xpath in self.paths_removed:
        #     del self.paths_removed[xpath]
        return True

    def create(self, xpath, keys=None, values=None, module=None, list_xpath=None):
        """
        To create a list item in the list /simplelist

        xpath:    /integrationtest:simplelist[simplekey='sdf']
        keys:     ('simplekey',),
                    tuple of keys in the order defined within yang.
        values:   [('simpleval', 18)],
                    list of (value, valtype) tuples

        module:   integrationtest

        In this case we store data in REDIS twice, once is to keep the order
        of the lists, and the second time to keep the data.
        """
        self.dirty = True
        xpath = "data" + xpath
        list_xpath = "metadata-listkey" + list_xpath
        self.log.trace("LIST-CREATE: %s [%s %s]", list_xpath, keys, values)

        if list_xpath not in self.paths_list_set:
            self.paths_list_set[list_xpath] = []
        if xpath not in self.paths_list_set[list_xpath]:
            self.paths_list_set[list_xpath].append(xpath)

        if list_xpath in self.paths_list_removed:
            if xpath in self.paths_list_removed[list_xpath]:
                self.paths_list_removed[list_xpath].remove(xpath)

        for i in range(len(keys)):
            (value, valtype) = values[i]
            self.log.trace("LIST-KEY: %s/%s => %s (%s)", xpath, keys[i], value, valtype)
            self.paths_set[xpath + "/"+keys[i]] = value

    def uncreate(self, xpath, list_xpath):
        """
        To remove a list item from the list /simplelist with the key sf

        xpath:   /integrationtest:simplelist[simplekey='sf']
        """
        self.dirty = True
        list_xpath = "metadata-listkey" + list_xpath
        xpath = "data" + xpath
        self.log.trace("UN-CREATE: %s [%s]", list_xpath, xpath)

        if list_xpath not in self.paths_list_removed:
            self.paths_list_removed[list_xpath] = []
        self.paths_list_removed[list_xpath].append(xpath)

        if list_xpath in self.paths_list_set:
            if xpath in self.paths_list_set[list_xpath]:
                self.paths_list_set[list_xpath].remove(xpath)

        return True

        raise NotImplementedError("uncreate not implemented")

    def set(self, xpath, value, valtype=18):
        self.dirty = True
        xpath = "data" + xpath
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
        xpath = "data" + xpath
        self.log.trace("GETS: %s", xpath)
        results = []
        (_, scan_results) = self.redis.zscan(xpath)
        for (result, _) in scan_results:
            results.append(result.decode('utf-8'))

        if xpath in self.paths_leaflist_removed:
            for value in self.paths_leaflist_removed[xpath]:
                if value in results:
                    results.remove(value)

        if xpath in self.paths_leaflist_set:
            for value in self.paths_leaflist_set[xpath]:
                if value not in results:
                    results.append(value)

        return results

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
        self.dirty = True
        xpath = "data" + xpath
        self.log.trace("ADD: %s => %s (valtype: %s)", xpath, value, valtype)

        if xpath not in self.paths_leaflist_set:
            self.paths_leaflist_set[xpath] = []
        self.paths_leaflist_set[xpath].append(value)

        if xpath in self.paths_leaflist_removed:
            if value in self.paths_leaflist_removed[xpath]:
                self.paths_leaflist_remove[xpath].remove(value)

        return True

    def remove(self, xpath, value):
        self.dirty = True
        xpath = "data" + xpath
        self.log.trace("REMOVE: %s <= %s", xpath, value)
        if xpath not in self.paths_leaflist_removed:
            self.paths_leaflist_removed[xpath] = []
        self.paths_leaflist_removed[xpath].append(value)

        if xpath in self.paths_leaflist_set:
            if value in self.paths_leaflist_set[xpath]:
                self.paths_leaflist_set[xpath].remove(value)

        return True

    def gets_unsorted(self, list_xpath, schema_path, ignore_empty_lists=False):
        """
        To retrieve a list of XPATH's as a generator to each list element in the list.
        The order remains in the order the user added items to the list.

        xpath:       /integrationtest:web/bands[name='Idlewild']/gigs
        schema_path: /integrationtest:web/integrationtest:bands/integrationtest:gigs

        returns a generator.
        """
        list_xpath = "metadata-listkey" + list_xpath
        self.log.trace("GETS_UNSORTED: %s ", list_xpath)

        removed_results = []
        if list_xpath in self.paths_list_removed:
            removed_results = self.paths_list_removed[list_xpath]

        (_, scan_results) = self.redis.zscan(list_xpath)
        for (result, _) in scan_results:
            xpath = result.decode('utf-8')
            if xpath not in removed_results:
                yield xpath

        if list_xpath in self.paths_list_set:
            for xpath in self.paths_list_set[list_xpath]:
                yield xpath

    def has_item(self, xpath, list_xpath):
        """
        Check to see if the list-element of a YANG list exists.

        xpath:          /integrationtest:simplelist[simplekey='b']
        """
        xpath = "data" + xpath
        list_xpath = "metadata-listkey" + list_xpath

        if list_xpath in self.paths_list_removed:
            if xpath in self.paths_list_removed[list_xpath]:
                return False
        if list_xpath in self.paths_list_set:
            if xpath in self.paths_list_set[list_xpath]:
                return True

        score = self.redis.zscore(list_xpath, xpath)
        if score:
            return True
        return False

    def get(self, xpath, default_value=None):
        xpath = "data" + xpath
        self.log.trace("GET: %s (default value: %s)", xpath, default_value)
        if xpath not in self.paths_removed:
            if xpath in self.paths_set:
                return self.paths_set[xpath]

            val = self.redis.get(xpath)
            if val:
                return val.decode('utf-8')
            if default_value:
                return default_value
        return None

    def delete(self, xpath):
        self.dirty = True
        xpath = "data" + xpath
        self.log.trace("DELETE: %s", xpath)
        self.paths_removed[xpath] = True
        if xpath in self.paths_set:
            del self.paths_set[xpath]
        return True

    def is_session_dirty(self):
        raise NotImplementedError("is_session_dirty not implemented")

    def has_datastore_changed(self):
        raise NotImplementedError("has_datastore_changed not implemented")

    def _check_deleted(self):
        return False

    def _check_changed(self):
        return False

    def _make_redis_key_safe(self, in_string):
        return in_string.replace('[', '\\[').replace('*', '\\*')

    def dump_xpaths(self):
        """
        Redis gives us everyhing in a non-deterministic order
        """
        results = {}
        for xpath in self.redis.keys("data/*"):
            xpath = xpath.decode('utf-8')
            real_xpath = xpath[xpath.find('/'):]
            results[real_xpath] = self.redis.get(self._make_redis_key_safe(xpath))

            print(real_xpath)
        print(results)
        raise NotImplementedError("dump_xpaths not implemented")

    def empty(self):
        self.log.warning("EMPTY: called")
        self.redis.flushall()
