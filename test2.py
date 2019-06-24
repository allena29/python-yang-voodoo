import Pyro4
ns = Pyro4.locateNS()
uri = ns.lookup("yangvooodoo.mellon-collie.net.yangvoodoo.dal.backend.bridge")
obj = Pyro4.Proxy(uri)
obj._pyroHmacKey = b"abc"

print(obj.get_fortune('sdf'))

for x in obj.get_generator('sdf'):
    print(x)
