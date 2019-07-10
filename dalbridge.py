#!/usr/bin/env python3
import Pyro4
import time
import threading
import traceback
from yangvoodoo.sysrepodal import SysrepoDataAbstractionLayer
from yangvoodoo.basedal import BaseDataAbstractionLayer
from yangvoodoo.Common import Utils


# TODO: we need to abstract data providers
import sysrepo as sr

exitFlag = 0


def module_change_cb(sess, module_name, event, private_ctx):
    print('MODULE CHANGE CB')


class change_subscriber(threading.Thread):

    def __init__(self, threadID, name, module):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.module = module
        self.dal = SysrepoDataAbstractionLayer()

    def run(self):
        conn = sr.Connection("test-daemon")
        session = sr.Session(conn)
        subscribe = sr.Subscribe(session)
        subscribe.module_change_subscribe(module, module_change_cb)
        # subscribe.dp_get_items_subscribe("/oven:oven-state", oven_state_cb)
        # sr.global_loop()
        while 1:
            print('.')
            time.sleep(1)

        print("Starting " + self.name)
        print('we have a dal', self.dal)
        time.sleep(5)
        print("Exiting " + self.name)


class DalSessionManager():

    def __init__(self):
        self.log = Utils.get_logger("DalSessionManager")
        self.sessions = {}

    def get_session(self, module, id):
        if id in self.sessions:
            self.log.info("Returning existing session for {0} <= {1}".format(id, self.sessions[id]))
            return self.sessions[id]

        session = SysrepoDataAbstractionLayer()
        session.connect(module, id)
        self.sessions[id] = session
        self.log.info("Creating new session for {0} => {1}".format(id, session))
        return session


class Dal():

    def __init__(self):
        global sessions
        self.id = None
        self.module = None

    @Pyro4.expose
    def connect(self, module, id):
        global sessions
        self.id = id
        self.module = module
        sessions.get_session(self.module, self.id)

    @Pyro4.expose
    def commit(self):
        global sessions
        try:
            session = sessions.get_session(self.module, self.id)
            return session.commit()
        except Exception:
            print("Pyro traceback:")
            print("".join(Pyro4.util.getPyroTraceback()))

    @Pyro4.expose
    def refresh(self):
        global sessions
        try:
            session = sessions.get_session(self.module, self.id)
            return session.refresh()
        except Exception:
            print("Pyro traceback:")
            print("".join(Pyro4.util.getPyroTraceback()))

    @Pyro4.expose
    def validate(self):
        print("Validate for id", self.id)
        global sessions
        session = sessions.get_session(self.module, self.id)
        return session.validate()

    @Pyro4.expose
    def set(self, xpath, value, valtype=18):
        global sessions
        session = sessions.get_session(self.module, self.id)
        return session.set(xpath, value, valtype)

    @Pyro4.expose
    def get(self, xpath, default_value=None):
        global sessions
        try:
            session = sessions.get_session(self.module, self.id)
            return session.get(xpath, default_value)
        except Exception:
            print("Pyro traceback:")
            print("".join(Pyro4.util.getPyroTraceback()))


if __name__ == '__main__':
    module = "integrationtest"

    thread1 = change_subscriber(1, "Thread-1", module)
    print('thread1 instantiated')
    thread1.start()
    print('thread1 started')
    print('about to join')
    # thread1.join()
    print('thread1 joined')

    sessions = DalSessionManager()

    daemon = Pyro4.Daemon(host='0.0.0.0')                # make a Pyro daemon
    daemon._pyroHmacKey = 'abc'
    ns = Pyro4.locateNS()                  # find the name server
    uri = daemon.register(Dal)   # register the greeting maker as a Pyro object
    ns.register("yangvooodoo.mellon-collie.net.yangvoodoo.dal.backend.bridge", uri)   # register the object with a name in the name server

    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls
