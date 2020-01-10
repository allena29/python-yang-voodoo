# REMOTE VOODOO Proof Of Concept

## Pyro4

[Pyro4](https://pythonhosted.org/Pyro4/intro.html]) allows for accessing objects over a network.
It has some constraints to help with security, such as not allowing access to dunder methods, which makes
it hard to use YANGVOODOO remotely because of the way yangvoodoo over-rides the python data model.

Pyro4 does not encrypt data, although it has a signing key for ensuring the data isn't tampered with.
wireshark shows an example of a set\_xpath. The signing key in this example code is a static string.

```
E@@`=RMT*'d'dPYRO0q5HMACPP-r:j_# serpent utf-8 python3.2 ('obj_0f5a037081354f8991a1038ba8e6b6fc','set',('/integrationtest:simpleleaf','ABC'),{})
```

Pyro4 runs a name-server which the servers register against and the client lookup
`net.mellon-collie.yangvooodoo.VoodooGatekeeper.127.0.0.1.integrationtest` is an object identifier and `PYRO:obj_45cded327537433b82c1c397a6f09075@127.0.0.1:54586` is a URI for the object.

```bash
py4ro-ns

pyro4-nsc list
--------START LIST
Pyro.NameServer --> PYRO:Pyro.NameServer@localhost:9090
    metadata: ['class:Pyro4.naming.NameServer']
net.mellon-collie.yangvooodoo.VoodooGatekeeper.127.0.0.1.integrationtest --> PYRO:obj_45cded327537433b82c1c397a6f09075@127.0.0.1:54586
net.mellon-collie.yangvooodoo.VoodooSchema.127.0.0.1.integrationtest --> PYRO:obj_3ab1c2f1ced64b42a2ad0f38a7589477@127.0.0.1:54586
net.mellon-collie.yangvooodoo.pyro4client.127.0.0.1.3946c94e-eac7-4a77-b52b-5ffb39b64918.integrationtest --> PYRO:obj_0f5a037081354f8991a1038ba8e6b6fc@127.0.0.1:54589
--------END LIST
```

## Architecture

The naming convention of the objects is

```
net.mellon-collie.yangvooodoo.<Function>.<HOSTNAME>.<YANG MODEL>
or
net.mellon-collie.yangvooodoo.<Function>.<HOSTNAME>.<UUID>.<YANG MODEL>
```


### Gatekeeper

The gatekeeper handles the following functions

- registers **VoodooGatekeeper** which allows clients to create a candidate transaction, and also manages persisting
  data. This maps to the object `yangvoodoo.Bridge.VoodooGatekeeper`
- registers **VoodooSchema** a read-only interface to read schema information.


The gatekeeper can be started wtih `datastore-client.py`. A pid flag is created
in `pid/<yangmodel>.pid`.




### Client Candidate Transactions

**NOTE: The gatekeeper will create this if `VoodooGatekepper.start_transaction()` is called**

The client creates is created with a *UUID*, it is possible to use the client object without ever persisting the data,
in which case the UUID doesn't matter (however the gatekeeper will use UUID's internally to give the ability for
multiple candidate transactions).

The client code can be started with `datastore-bridge.py <uuid>`

This implements the same functions a dal implements.


### Example


```python
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
```


##### Logs from the Gatekeeper

```
2020-01-10 23:07:47,046 - DalGatekeeper   INFO          Created new candidate session:b737f052-fa0f-4206-ab8a-f32629eea877 for:integrationtest
2020-01-10 23:07:47,187 - b737f052-fa0f-4206-ab8a-f32629eea877 INFO          Initialising datastore with yang model integrationtest
2020-01-10 23:07:47,197 - b737f052-fa0f-4206-ab8a-f32629eea877 INFO          Connected yang and created self.datastore
2020-01-10 23:07:47,197 - b737f052-fa0f-4206-ab8a-f32629eea877 WARNING       No startup datafile exists
2020-01-10 23:07:47,205 - b737f052-fa0f-4206-ab8a-f32629eea877 INFO          Registered: net.mellon-collie.yangvooodoo.VoodooClient.127.0.0.1.b737f052-fa0f-4206-ab8a-f32629eea877.integrationtest via 127.0.0.1
2020-01-10 23:07:47,206 - b737f052-fa0f-4206-ab8a-f32629eea877 INFO          Running as PID: 30943 for integrationtest
2020-01-10 23:07:47,555 - b737f052-fa0f-4206-ab8a-f32629eea877 DEBUG         datastore_bridge: object_id <yangvoodoo.Bridge.VoodooClient object at 0x10f5fb438> in pid 30943
2020-01-10 23:07:47,555 - b737f052-fa0f-4206-ab8a-f32629eea877 DEBUG         datastore_bridge; <yangvoodoo.stublydal.StubLyDataAbstractionLayer object at 0x10f453438>
2020-01-10 23:07:47,556 - b737f052-fa0f-4206-ab8a-f32629eea877 DEBUG         pyro4 get: /integrationtest:simpleleaf (default: None)
2020-01-10 23:07:47,557 - b737f052-fa0f-4206-ab8a-f32629eea877 DEBUG         pyro4 get: /integrationtest:simpleleaf (default: None)
```
