# saved as greeting-server.py
import Pyro4


class bridge:

    def __init__(self):
        print('bridge is', self)


b = bridge()


class SysrepoDal(object):

    def __init__(self):
        global b
        print('self is ok becuase expose tag is not ste - but every instance is a new object')
        print('b', b)

    def x(self):
        print('sdf123')

    def _y(self):
        print('y', self)

    @Pyro4.expose
    def get_generator(self, name):
        for x in range(50):
            yield str(x)

    @Pyro4.expose
    def get_fortune(self, name):
        self.x()

        self._y()
        print('name', name)
        print(Pyro4.current_context.client_sock_addr)
        return "Hello, {0}. Here is your fortune message:\n" \
               "Tomorrow's lucky number is 12345678.".format(name)


daemon = Pyro4.Daemon(host='192.168.3.1')                # make a Pyro daemon
daemon._pyroHmacKey = 'abc'
ns = Pyro4.locateNS()                  # find the name server
uri = daemon.register(SysrepoDal)   # register the greeting maker as a Pyro object
ns.register("yangvooodoo.mellon-collie.net.yangvoodoo.dal.backend.bridge", uri)   # register the object with a name in the name server

print("Ready.")
daemon.requestLoop()                   # start the event loop of the server to wait for calls
