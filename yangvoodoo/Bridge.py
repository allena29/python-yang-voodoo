import atexit
import os
import sys
import time


import Pyro4
import yangvoodoo
from yangvoodoo.stublydal import StubLyDataAbstractionLayer

sys.path.append('/Users/adam/python-yang-voodoo')


class LibyangDataStore:

    DATA_FILE_FORMAT = 1

    def __init__(self):
        self.log = yangvoodoo.Common.Utils.get_logger('DalBridge')

    def connect(self, yang_model, yang_location=None, data_location='datastore/'):
        self.log.info('Initialising datastore with yang model %s', yang_model)
        self.datastore = yangvoodoo.stublydal.StubLyDataAbstractionLayer()
        self.datastore.connect(yang_model, yang_location)
        self.data_location = data_location
        self.yang_model = yang_model

        if not os.path.exists(self.data_location + self.yang_model + '.startup'):
            self.log.warning('No startup datafile exists')
        else:
            self.log.info('Loading startup data from: %s%s.startup', self.data_location,
                          self.yang_model)
            self.datastore.load(self.data_location + self.yang_model + '.startup')

    def shutdown(self):
        try:
            self.datastore.dump(self.data_location + self.yang_model + '.persist')
            self.log.info('Persisted data to: %s%s.persist', self.data_location, self.yang_model)
        except TypeError:
            self.log.warning('Data not persisted to disk - the datastore may have been blank.')


datastore_bridge = LibyangDataStore()


@atexit.register
def cleanexit():
    datastore_bridge.log.info('Please wait- persisting data')
    datastore_bridge.shutdown()


class Pyro4Bridge:

    def __init__(self):

        global datastore_bridge
        self.datastore = datastore_bridge

    @Pyro4.expose
    def container(self, xpath):
        return datastore_bridge.datastore.container(xpath)

    @Pyro4.expose
    def create_container(self, xpath):
        return datastore_bridge.datastore.create_container(xpath)

    @Pyro4.expose
    def create(self, xpath, keys, values, module):
        return datastore_bridge.datastore.create(xpath, keys, values, module)

    @Pyro4.expose
    def uncreate(self, xpath):
        return datastore_bridge.datastore.uncreate(xpath)

    @Pyro4.expose
    def gets(self, xpath):
        return datastore_bridge.datastore.gets(xpath)

    @Pyro4.expose
    def add(self, xpath, value, valtype):
        return datastore_bridge.datastore.add(xpath, value, valtype)

    @Pyro4.expose
    def remove(self, xpath, value):
        return datastore_bridge.datastore.remove(xpath, value)

    @Pyro4.expose
    def set(self, xpath, value, valtype=18, nodetype=4):
        datastore_bridge.datastore.set(xpath, value, valtype=18, nodetype=4)

    @Pyro4.expose
    def gets_len(self, xpath):
        datastore_bridge.log.debug('%s: GETS_LEN: %s', self, xpath)
        return datastore_bridge.datastore.gets_len(xpath)

    @Pyro4.expose
    def has_item(self, xpath):
        return datastore_bridge.datastore.has_item(xpath)

    @Pyro4.expose
    def gets_unsorted(self, xpath, schema_path, ignore_empty_lists=False):
        return datastore_bridge.datastore.gets_unsorted(xpath, schema_path, ignore_empty_lists)

    @Pyro4.expose
    def get(self, xpath, default_value):
        datastore_bridge.log.debug('%s: GET: %s (default: %s', self, xpath, default_value)
        return datastore_bridge.datastore.get(xpath, default_value)

    @Pyro4.expose
    def dumps(self, format):
        return datastore_bridge.datastore.dumps(format)


def startup(yang_model, yang_location=None, hostname='192.168.3.1', nameserver='192.168.1.28',
            hmac_key='this-value-is-a-dummy-hmac-key'):
    object_id = "net.mellon-collie.yangvooodoo.pyro4bridge." + hostname
    datastore_bridge.connect(yang_model, yang_location)
    daemon = Pyro4.Daemon(host=hostname)
    daemon._pyroHmacKey = hmac_key
    ns = Pyro4.locateNS(nameserver)
    datastore_bridge.log.info("Registered: %s via %s", object_id, nameserver)
    uri = daemon.register(Pyro4Bridge)
    ns.register(object_id, uri)

    daemon.requestLoop()                   # start the event loop of the server to wait for calls
