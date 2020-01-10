import time
import Pyro4


ns = Pyro4.locateNS()
hostname = '127.0.0.1'
hmac_key = 'this-value-is-a-dummy-hmac-key'
yang_model = 'integrationtest'

object_id = "net.mellon-collie.yangvooodoo.VoodooGatekeeper." + hostname + '.' + yang_model
uri = ns.lookup(object_id)
gatekeeper_remote_obj = Pyro4.Proxy(uri)
print('VoodooGatekeeper')
print('object_id:', object_id)
print('uri:', uri)
gatekeeper_remote_obj._pyroHmacKey = hmac_key
uuid = gatekeeper_remote_obj.start_transaction()
print('-------')
print('UUID for our transaction', uuid)
print('-------')

# Note: it takes time to spawn this object
time.sleep(0.5)

object_id = "net.mellon-collie.yangvooodoo.VoodooClient." + hostname + '.' + uuid + '.' + yang_model
uri = ns.lookup(object_id)
print('VoodooClient', uuid)
print('object_id:', object_id)
print('uri:', uri)
client_remote_obj = Pyro4.Proxy(uri)
client_remote_obj._pyroHmacKey = hmac_key
xpath = '/integrationtest:simpleleaf'
print(client_remote_obj.get(xpath))
client_remote_obj.set(xpath, 'hello!')
print('just set a value')
print(client_remote_obj.get(xpath))
print(client_remote_obj.dumps(2))
