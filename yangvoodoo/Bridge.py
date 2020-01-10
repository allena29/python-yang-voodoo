import os
import subprocess
import sys
import time
import uuid

import Pyro4

sys.path.append('/Users/adam/python-yang-voodoo')
import yangvoodoo
from yangvoodoo.stublydal import StubLyDataAbstractionLayer

# Dont like these global variables
data_location = None
open_threads = {}
yang_model = None
yang_location = None
ns = None
daemon = None
hmac_key = None
nameserver = None
hostname = None
log = yangvoodoo.Common.Utils.get_logger('unknown')
# This could be a LibyangDataStore
# if we want read onl datain the future
datastore_bridge = None


class LibyangDataStore:

    DATA_FILE_FORMAT = 1

    def __init__(self):
        self.log = log
        self.connected = False

    def connect(self):
        self.log.info('Initialising datastore with yang model %s', yang_model)
        self.datastore = yangvoodoo.stublydal.StubLyDataAbstractionLayer()
        self.datastore.connect(yang_model, yang_location)
        self.data_location = data_location
        self.log.info('Connected yang and created self.datastore')
        file_location = self.data_location + yang_model + '.persist'
        self._check_data_file_size_and_cleanup_if_empty(file_location)

        if not os.path.exists(file_location):
            self.log.warning('No startup datafile exists')
        else:
            self.log.info('Loading startup data from: %s%s.persist', self.data_location,
                          yang_model)
            self.datastore.load(file_location)
        self.connected = True

    def _check_data_file_size_and_cleanup_if_empty(self, file_location):
        if not os.path.exists(file_location):
            return False
        if os.stat(file_location).st_size == 0:
            os.remove(file_location)
            self.log.warning('Datafile was empty - removed')
        return True

    def shutdown(self):
        if not self.connected:
            return
        file_location = data_location + yang_model + '.persist'
        try:
            self.datastore.dump(file_location)
            self.log.info('Persisted data to: %s%s.persist', data_location, yang_model)
        except TypeError:
            self.log.warning('Data not persisted to disk - the datastore may have been blank.')
        self._check_data_file_size_and_cleanup_if_empty(file_location)


# @atexit.register
def cleanexit(a, b):
    print('Trying to clean exit' + str(yang_model))

    if datastore_bridge:
        log.info('Please wait- persisting data')
        datastore_bridge.shutdown()
    if yang_model:
        pid_file = 'pid/' + yang_model + '.pid'
        if os.path.exists(pid_file):
            os.remove(pid_file)
    sys.exit()


class VoodooGatekeeper:

    """
    Uses to provide an entry point for remote pyro4 clients to create candidate transactions.

    TBD:we might make this something which gives a read-only view of the running datastore.
    Although that might be too hard
    """

    def __init__(self):
        self.log = yangvoodoo.Common.Utils.get_logger('DalGatekeeper')

    @Pyro4.expose
    def start_transaction(self):
        """
        This here does not work..

        We probabl have to use multiprocessing and *subprocess* ourselves
        for this to work.

        Assumption is a pyro4 exposed thing shouldn't register more pyro4 objects.
        """
        self.uuid = str(uuid.uuid4())
        session_flag = "candidate/%s.session" % (self.uuid)
        with open(session_flag, 'w') as fh:
            self.log.info("Created new candidate session:%s for:%s", self.uuid, yang_model)
            proc = subprocess.Popen(['/usr/bin/env', 'python3', 'datastore-bridge.py', self.uuid])
            fh.write(str(proc.pid))
        return self.uuid


class VoodooSchema:

    def __init__(self):
        self.session = yangvoodoo.DataAccess()
        self.session.connect(yang_model, yang_location)
        self.log = log

    @Pyro4.expose
    def schema(self):
        self.log.info('Schema thing')


class VoodooClient(VoodooSchema):

    """
    """

    def __init__(self):
        self.datastore_bridge = datastore_bridge
        self.session = self.datastore_bridge.datastore
        self.log = log
        self.log.debug('datastore_bridge: object_id %s in pid %s', self, os.getpid())
        self.log.debug('datastore_bridge; %s', self.session)

    @Pyro4.expose
    def dbg_dump(self):
        self.log.debug(str(self.datastore_bridge.datastore.dumps()))

    @Pyro4.expose
    def container(self, xpath):
        return self.datastore_bridge.datastore.container(xpath)

    @Pyro4.expose
    def create_container(self, xpath):
        return self.datastore_bridge.datastore.create_container(xpath)

    @Pyro4.expose
    def create(self, xpath, keys, values, module):
        return self.datastore_bridge.datastore.create(xpath, keys, values, module)

    @Pyro4.expose
    def uncreate(self, xpath):
        return self.datastore_bridge.datastore.uncreate(xpath)

    @Pyro4.expose
    def gets(self, xpath):
        return self.datastore_bridge.datastore.gets(xpath)

    @Pyro4.expose
    def add(self, xpath, value, valtype):
        return self.datastore_bridge.datastore.add(xpath, value, valtype)

    @Pyro4.expose
    def remove(self, xpath, value):
        return self.datastore_bridge.datastore.remove(xpath, value)

    @Pyro4.expose
    def set(self, xpath, value, valtype=18, nodetype=4):
        return self.datastore_bridge.datastore.set(xpath, value, valtype=18, nodetype=4)

    @Pyro4.expose
    def gets_len(self, xpath):
        return self.datastore_bridge.datastore.gets_len(xpath)

    @Pyro4.expose
    def has_item(self, xpath):
        return self.datastore_bridge.datastore.has_item(xpath)

    @Pyro4.expose
    def gets_unsorted(self, xpath, schema_path, ignore_empty_lists=False):
        return self.datastore_bridge.datastore.gets_unsorted(xpath, schema_path, ignore_empty_lists)

    @Pyro4.expose
    def get(self, xpath, default_value=None):
        self.log.debug('pyro4 get: %s (default: %s)', xpath, default_value)
        return self.datastore_bridge.datastore.get(xpath, default_value)

    @Pyro4.expose
    def dumps(self, format):
        return self.datastore_bridge.datastore.dumps(format)


def startup_gatekeeper(our_yang_model, our_yang_location=None, our_hostname='192.168.3.1',
                       our_nameserver='192.168.1.28',
                       our_hmac_key='this-value-is-a-dummy-hmac-key', our_data_location='datastore/'):
    global yang_model, yang_location, hostname, nameserver, hmac_key, data_location, log, daemon, ns
    yang_model = our_yang_model
    yang_location = our_yang_location
    hostname = our_hostname
    nameserver = our_nameserver
    hmac_key = our_hmac_key
    data_location = our_data_location
    log = yangvoodoo.Common.Utils.get_logger('DalBridge')
    pid_file = 'pid/%s.pid' % (yang_model)
    if os.path.exists(pid_file):
        os.remove(pid_file)
    object_id = "net.mellon-collie.yangvooodoo.VoodooGatekeeper." + hostname + '.' + yang_model
    # Assuming right now we won't need this
    # datastore_bridge.connect(yang_model, yang_location)
    daemon = Pyro4.Daemon(host=hostname)
    daemon._pyroHmacKey = hmac_key
    ns = Pyro4.locateNS(nameserver)
    log.info("Registered: %s via %s", object_id, nameserver)
    uri = daemon.register(VoodooGatekeeper)
    ns.register(object_id, uri)

    object_id = "net.mellon-collie.yangvooodoo.VoodooSchema." + hostname + '.' + yang_model
    uri = daemon.register(VoodooSchema)
    ns.register(object_id, uri)

    our_pid = os.getpid()
    with open(pid_file, 'w') as pid_flag:
        pid_flag.write(str(our_pid))

    log.info('Running as PID: %s for %s', our_pid, yang_model)

    daemon.requestLoop()                   # start the event loop of the server to wait for calls


def startup_client(uuid, our_yang_model, our_yang_location=None, our_hostname='192.168.3.1',
                   our_nameserver='192.168.1.28',
                   our_hmac_key='this-value-is-a-dummy-hmac-key', our_data_location='datastore/'):
    """
    Startup a libyang data tree a a client user.
    """
    global yang_model, yang_location, hostname, nameserver, hmac_key, data_location, log, daemon, ns, datastore_bridge
    yang_model = our_yang_model
    yang_location = our_yang_location
    hostname = our_hostname
    nameserver = our_nameserver
    hmac_key = our_hmac_key
    data_location = our_data_location
    log = yangvoodoo.Common.Utils.get_logger(uuid)
    object_id = "net.mellon-collie.yangvooodoo.VoodooClient." + hostname + '.' + uuid + '.' + yang_model
    datastore_bridge = LibyangDataStore()
    datastore_bridge.connect()
    daemon = Pyro4.Daemon(host=hostname)
    daemon._pyroHmacKey = hmac_key
    ns = Pyro4.locateNS(nameserver)
    log.info("Registered: %s via %s", object_id, nameserver)
    uri = daemon.register(VoodooClient)
    ns.register(object_id, uri)
    our_pid = os.getpid()

    log.info('Running as PID: %s for %s', our_pid, yang_model)

    daemon.requestLoop()                   # start the event loop of the server to wait for calls
