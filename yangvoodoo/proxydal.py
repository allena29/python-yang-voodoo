import yangvoodoo
import yangvoodoo.basedal
import yangvoodoo.stubdal
from yangvoodoo.Common import Utils


class ProxyDataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):

    """
    This method will provide a cache around a datastore.
    """

    DAL_ID = "ProxyDAL"

    def __init__(self, realstore, log=None):
        super().__init__(log)
        if not log:
            log = Utils.get_logger("Proxy" + realstore.DAL_ID)
        self.log = log
        self.cache = yangvoodoo.stubdal.StubDataAbstractionLayer()
        self.store = realstore
        self.module = None
        self.refresh()

    def connect(self, module, tag='<id-tag>'):
        self.cache.connect(module, tag)
        self.module = module
        return self.store.connect(module, tag)

    def disconnect(self):
        self.cache.disconnect()
        return self.store.disconnect()

    def commit(self):
        try:
            self.cache.commit()
        except yangvoodoo.Errors.NothingToCommit:
            pass
        return self.store.commit()

    def validate(self):
        self.cache.validate()
        return self.store.validate()

    def container(self, xpath):
        if xpath not in self.value_cached:
            result = self.store.container(xpath)
            self.value_cached[xpath] = result
        return self.value_cached[xpath]

    def create_container(self, xpath):
        self.cache.create_container(xpath)
        self.value_cached[xpath] = True
        return self.store.create_container(xpath)

    def create(self, xpath, keys=[], values=[], list_xpath=None):
        self.has_item_cached = {}
        self.unsorted_cached = {}
        self.sorted_cached = {}
        self.len_cached = {}
        self.cache.create(xpath, keys, values, list_xpath=list_xpath)
        return self.store.create(xpath, keys, values, list_xpath=list_xpath)

    def uncreate(self, xpath, keys=[], values=[], module=None, list_xpath=None):
        self.has_item_cached = {}
        self.unsorted_cached = {}
        self.sorted_cached = {}
        self.len_cached = {}
        self.cache.uncreate(xpath, list_xpath=list_xpath)
        return self.store.uncreate(xpath, list_xpath=list_xpath)

    def add(self, xpath, value, valtype):
        self.cache.add(xpath, value, valtype)
        return self.store.add(xpath, value, valtype)

    def remove(self, xpath, value):
        self.cache.remove(xpath, value)
        self.refresh()
        return self.store.remove(xpath, value)

    def gets(self, xpath):
        if xpath not in self.value_cached:
            items = list(self.store.gets(xpath))
            self.value_cached[xpath] = items
        for val in self.value_cached[xpath]:
            yield val

    def has_item(self, xpath, list_xpath):
        if xpath not in self.has_item_cached:
            result = self.store.has_item(xpath, list_xpath)
            self.has_item_cached[xpath] = result
        return self.has_item_cached[xpath]

    def set(self, xpath, value, valtype=0):
        self.cache.set(xpath, value, valtype)
        if valtype == 5:
            value = True
        self.value_cached[xpath] = value
        if valtype == 5:
            value = None
        return self.store.set(xpath, value, valtype)

    def gets_sorted(self, list_xpath, schema_xpath, ignore_empty_lists=False):
        if list_xpath not in self.sorted_cached:
            items = list(self.store.gets_sorted(list_xpath, schema_xpath, ignore_empty_lists=ignore_empty_lists))
            self.sorted_cached[list_xpath] = items
        for xpath in self.sorted_cached[list_xpath]:
            if not self.store.DAL_IN_MEMORY:
                self._speculative_create_list_keys(xpath, schema_xpath)
            yield xpath

    def gets_unsorted(self, list_xpath, schema_xpath, ignore_empty_lists=False):
        # raise ValueError(list_xpath + "  " + schema_xpath, self.)
        """
         ('/integrationtest:web/bands', '/integrationtest:web/integrationtest:bands')

         ("/integrationtest:web/bands[name='Longpigs']/gigs", '/integrationtest:web/integrationtest:bands/integrationtest:gigs')

         """
        if list_xpath not in self.unsorted_cached:
            items = list(self.store.gets_unsorted(list_xpath, schema_xpath, ignore_empty_lists=ignore_empty_lists))
            self.unsorted_cached[list_xpath] = items

        for xpath in self.unsorted_cached[list_xpath]:
            if not self.store.DAL_IN_MEMORY:
                self._speculative_create_list_keys(xpath, schema_xpath)
            yield xpath

    def gets_len(self, list_xpath):
        if list_xpath not in self.len_cached:
            result = self.store.gets_len(list_xpath)
            self.len_cached[list_xpath] = result
        return self.len_cached[list_xpath]

    def _speculative_create_list_keys(self, xpath, schema_xpath):
        """

        So gets_unsorted is called with
                 ("/integrationtest:web/bands[name='Longpigs']/gigs", '/integrationtest:web/integrationtest:bands/integrationtest:gigs')

        """
        (p, keys, vals) = yangvoodoo.Common.Utils.decode_xpath_predicate(xpath)
        for index in range(len(keys)):
            key_schema_path = schema_xpath + "/" + self.module+":"+keys[index]
            valtype = Utils.get_yang_type_from_path(self.context, key_schema_path, vals[index])
            val = Utils.convert_string_to_python_val(vals[index], valtype)

            key_path = xpath + "/" + keys[index]
            self.value_cached[key_path] = val

    def get(self, xpath, default_value=None):
        if xpath not in self.value_cached:
            item = self.store.get(xpath, default_value)
            self.value_cached[xpath] = item
        return self.value_cached[xpath]

    def delete(self, xpath):
        self.cache.delete(xpath)
        self.store.delete(xpath)
        self.refresh()

    def refresh(self):
        self.cache.empty()
        self.value_cached = {}
        self.unsorted_cached = {}
        self.sorted_cached = {}
        self.has_item_cached = {}
        self.len_cached = {}

    def is_session_dirty(self):
        return self.store.is_session_dirty()

    def has_datastore_changed(self):
        return self.store.has_datastore_changed()

    def dump_xpaths(self):
        return self.store.dump_xpaths()
