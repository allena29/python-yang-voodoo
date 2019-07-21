# Scaling YANG model

see `test/scaling` which can be manually run, using a stub datastore the following values are found with commit `ce5306edd19c3b355620ccb36324841ccb7d08b2`

|Test                                                  | Paths     | Time (seconds) |
|------------------------------------------------------|-----------|----------------|
| One entry to thirty nested lists                     | 30        | 0.005          |
| One hundred entries to thirty nested lists           | 3000      | 0.422          |
| Add nested leaves with deep data set (               | 16100     | 1.25           |
| Dump xpaths with                                     | 16100     | 0.008          |
| Dump XPATHS to template                              | 16100     | 1.72           |
| Load XPATHS from xml                                 | 16100     | 0.720          |
| Add three thousand entries to one list               | 3000      | 0.175          |
| Simple leaf changed 3000 times                       | 3000      | 0.06           |


Factors affecting performance

 - Deepness of the XPATH - shallow data is easier to store. (There are a few areas of processing of predicates which looks to be repetitive)
 - When writing an XML template we look for a cache hit on the parent nodes, if there is data access to siblings within the same parent we have less work to do.

# Optimisation for stub-store creating list keys

The following patch gives a small improvement using the stub 

```python
@@ -114,12 +114,7 @@ class StubDataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):

         self.log.trace('CREATE-LIST-ELEMENT: %s (keys: %s, values: %s)', xpath, keys, values)
         self.dirty = True
-        predicates = ""
-        for index in range(len(keys)):
-            (value, valuetype) = values[index]
-            predicates = predicates + "["+keys[index]+"='"+str(value)+"']"

-        list_xpath = xpath.replace(predicates, '')
         if list_xpath not in self.list_element_map:
             self.list_element_map[list_xpath] = []
         self.list_element_map[list_xpath].append(xpath)
@@ -129,7 +124,7 @@ class StubDataAbstractionLayer(yangvoodoo.basedal.BaseDataAbstractionLayer):
             (value, valuetype) = values[index]
             self.set(xpath + "/" + keys[index], value, valuetype)
```

|Test                                                  | Paths     | Time (seconds) | with parentnode optimisation |
|------------------------------------------------------|-----------|----------------|------------------------------|
| One entry to thirty nested lists                     | 30        | 0.005          | 0.004                        |
| One hundred entries to thirty nested lists           | 3000      | 0.422          | 0.41                         |
| Add nested leaves with deep data set (               | 16100     | 1.25           | 1.22                         |
| Dump xpaths with                                     | 16100     | 0.008          | 0.0073                       |
| Dump XPATHS to template                              | 16100     | 1.72           | 1.71                         |
| Load XPATHS from xml                                 | 16100     | 0.720          | 0.69                         |
| Add three thousand entries to one list               | 3000      | 0.175          | 0.167                        |
| Simple leaf changed 3000 times                       | 3000      | 0.06           | 0.059                        |





# Summary

- The results below are center towards reading and list iteration, the average speed is from 20,000 operations.
- The results are based on the test scenario in `timing.py`, the benefits from any of the optimisation is only gained if data that has been cached/pre-fetched is actually accessed.


These values come from sysrepo running within Docker on a Intel i7-7820HQ (approx 23% slower in docker)


| Speed (ms per operation)     | Scenario                       |
|------------------------------|--------------------------------|
| 1.21                         | sysrepo alone                  |
| 0.66                         | with proxy lazy cache*         |
| 0.21                         | with proxy and type-blind speculative creation of list keys\** |
| 0.38                         | with proxy and type-correct speculative creation of list keys\***  |
| 0.12                         | stub based datastore (python dict based)       |
| 0.14                         | stub based datastore with proxy and type-correct speculative creation of list keys\*** |
| 0.9                          | sysrepo with proxy lazy cache and refactored libyang lookups - but no speculative creating of list keys |
| 0.35                         | sysrepo with proxy lazy cache and refactored libyang lookups - and type correct speculative lookups |
| 0.07                         | stub with proxy lazy cache and refactored libyang lookups - but no speculative creating of list keys |
| 0.09                         | stub with proxy lazy cache and refactored libyang lookups - and type correct speculative lookups \**** |


- \* the first version of the proxy cache is lazy, when deleting, adding items to lists parts of the cache are flushed.

- \** around 20 us per key to pre-populate *if* we don't care about the type of keys, i.e. if we re-enable this we will show list-keys as, integers

- \*** when we pre-populate list keys with the correct type it's a bit slower

- \**** because this is slower with speculative caching of list keys now we categorise the DAL as IN MEMORY or not - we only do specualtive_caching of list_keys for DAL's that are not IN MEMORY


## Test

 - Opening a session and getting a root node (1-3ms)
 - Simple get of leaves CACHE-MISS (~ 1ms per item)
 - Spin around a list CACHE-MISS (4.3ms for a list of 250 elements)
 - Spin around a list CACHE-HIT (0.3ms for a list of 250 elements)
 - Length of a list CACHE-HIT (0.1ms)


# Slight improvement with caching the schema nodes - 30 microseconds
