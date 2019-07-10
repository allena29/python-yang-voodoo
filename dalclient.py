import Pyro4
import sys

ns = Pyro4.locateNS()
uri = ns.lookup("yangvooodoo.mellon-collie.net.yangvoodoo.dal.backend.bridge")
obj = Pyro4.Proxy(uri)
obj._pyroHmacKey = b"abc"

id = sys.argv[1]
print(obj.connect("integrationtest", id))
path = "/integrationtest:simpleenum"
print(obj.get(path))
obj.set(path, "B", 11)
obj.validate()
