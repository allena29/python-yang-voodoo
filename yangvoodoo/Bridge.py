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
    def test(self, name):
        print(self.datastore)

        for x in range(5):
            yield str(x)


def startup(yang_model, yang_location=None, hostname='192.168.3.1', nameserver='192.168.1.28'):
    object_id = "net.mellon-collie.yangvooodoo.pyro4bridge." + hostname
    datastore_bridge.connect(yang_model, yang_location)
    daemon = Pyro4.Daemon(host=hostname)
    daemon._pyroHmacKey = 'WRONG'
    ns = Pyro4.locateNS(nameserver)
    datastore_bridge.log.info("Registered: %s via %s", object_id, nameserver)
    uri = daemon.register(Pyro4Bridge)
    ns.register(object_id, uri)

    daemon.requestLoop()                   # start the event loop of the server to wait for calls
