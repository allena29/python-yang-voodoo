import Pyro4
ns = Pyro4.locateNS()
hostname = '127.0.0.1'
hmac_key = 'this-value-is-a-dummy-hmac-key'
uri = ns.lookup("net.mellon-collie.yangvooodoo.pyro4gatekeeper." + hostname + '.integrationtest')
obj = Pyro4.Proxy(uri)
obj._pyroHmacKey = hmac_key


connection = obj.connect('integrationtest')
print(connection)

# Currently what we have implemented here is on startup the bridge creates
# a single libyang datatree. So pyro4 doesn't actually expose connect itself.
# What this should mean is that we have access to a global libyang data tree
# without having to keep our own things.
# *IF* however we want to work in our own private candidate transaction we
# need more things.
# On startup we load a file called .startup if it exists.
# When we have interesting changes we save it to a .persist.
# We are not guarneteed to have a persist file at a moment in time thought.
# So if we want to create a candidate transaction we need to create a
# unique instance of a libyang datatree, sourced based on the persist or
# startup files (perhaps we should always create a persist file when the
# bridge comes to life).
# Next... We need to some kind of locking thing which says if we have created
# a cndidate transacton we a) can know if somethign has changed snice we
# last built our libyang data tree. and second we can do a meaningful refresh
# A sensible assumptio is that if we are keeping a long lived *candidate*
# transaction open we won't ahve a large number of XPATH's that have changed.
# so in that case we probably just track every xpath we set/create and if we
# call refresh then just simple do a load() back on the .persist file.
