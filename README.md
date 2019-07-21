# Python access to YANG based Datastore (based on libyang/sysrepo)

[![](https://travis-ci.org/allena29/python-yang-voodoo.svg?branch=master)](https://travis-ci.org/allena29/python-yang-voodoo)
[![Coverage Status](https://coveralls.io/repos/github/allena29/python-yang-voodoo/badge.svg?branch=master)]

The aim of this project is to provide the ability to write python code where there is a strong YANG based data model.
By providing an object based access layer it allows data to be traversed without worrying about lower level details, and
allow a stronger focus on getting the 'value add' correct.

To see screencasts demonstrating the concepts see:

 - [36 second spinning up docker](https://asciinema.org/a/246485) - uses this [yang model](https://raw.githubusercontent.com/allena29/python-yang-voodoo/master/yang/integrationtest.yang) and [initial data](https://raw.githubusercontent.com/allena29/python-yang-voodoo/master/init-data/integrationtest__webdata.xml)
 - [12min showing details usage](https://asciinema.org/a/246248)

A powerpoint slide:

[https://app.box.com/s/lzwmumytlbbo83eew0etcpq6qtqjmywl](https://app.box.com/s/lzwmumytlbbo83eew0etcpq6qtqjmywl)


Taking the very basic yang module below, we can imagine how it might look in a few different ways.

```
container bronze {
  container silver {
    container gold {
      container platinum {
        leaf deep {
          type string;
        }
      }
    }
  }
}
```


This project builds upon [Sysrepo](http://www.sysrepo.org/) as the **default** datastore, and [Libyang](https://github.com/CESNET/libyang) to tightly couple the data model to a set of standard yang models. [lxml](https://lxml.de/index.html) is used for processing of templates.



```python
root.bronze.silver.gold.platinum.deep = 'DOWN'
print(root.bronze.silver.gold.platinum.deep)
```

We can then imagine other ways we might WRITE and READ this data, if this was a database backend like SQL we might access the data as.

```sql
UPDATE bronze_silver_gold_platinum SET deep = 'DOWN';
SELECT deep FROM bronze_silver_gold_platinum;
```

Or perhaps with the sysrepo vanilla python bindings with XPATH.

```python
session.set_item('/module:bronze/silver/gold/platinum/deep', 'DOWN'. sr.SR_STRING_T)

item = session.get_item('/module:bronze/silver/gold/platinum/deep')
print(item.val_to_string)
```

Or Perhaps modelled as xml

```xml
  <bronze>
    <silver>
      <gold>
        <platinum>
          <deep>DOWN</deep>
        </platinum>
      </gold>
    </silver>
  </bronze>
```

 Or json

 ```json
  {
    "bronze" : {
      "silver": {
        "gold": {
          "platinum": {
            "deep": "down"
          }
        }
      }
    }
  }
 ```


# Overall Structure


![](Documentation/overview.png)


## Abstraction of Data Access

This project was written around sysrepo for data storage, however there is no strong dependency on using sysrepo. In order to support unit testing of code there is already an alternative datastore provided as **stubdal** (although that is not production grade).

Implementing a new data_abastraction_layer is as simple as implementing the following methods.

 - **connect()** - connects to the datastore, it is expected that the datastore may provide and track a specific connection providing *transactionality*. Takes in the arguments of `yang module` and `yang_location`
 - **validate()** - validate pending changes are valid based on the full data of the entire datastore (VoodooNode is limited to validating the yang schema itself).
 - **refresh()** - refresh the data from the datastore, the datastore may provide us with the data present in the datastore at the time we first connected, or it may refresh in realtime everytime we access a given set of data.
 - **commit()** - commit pending datastore.
 - **disconnect()** - disconnect from the datastore
 - **is_session_dirty()** - indicates we have made changes
 - **has_datastore_changed()** - indicates changes have been made to the datastore from a different transaction.
 - **container(xpath)** - returns True/False if the presence-container exists.
 - **get(xpath, default_value)** - get specific data by XPATH, this will not apply to non-presence containers or lists
 - **gets_unsorted(list_xpath, schema_path, ignore_empty_lists)** - get a list of XPATH's representing the items in the list, it is expected the datastore will maintain the order the user inserts the data and this MUST return the data in that order. If the list is empty this method will normally raise an ListDoesNotContainElement exception.
 - **gets_sorted(list_xpath, schema_path, ignore_empty_lists)** - as gets_unsorted, but the results will be sorted by XPATH.
 - **gets_len(list_xpath)** - gets back number of list elements available in the list (Not for leaf-lists)
 - **gets(xpath)** - gets a generator back of values for a specific XPATH (leaf lists only)
 - **add(xpath, value, valuetype)** - add a new entry to the end of a leaf-list at the given XPATH
 - **remove(xpath, value)** - remvoes an entry from a leaf-list at the given XPATH - the XPATH given is the XPATH to the leaf-list itself, not the specific item.
 - **has_item(xpath, list_xpath)**- returns True if the item has been populated with data.
 - **create(xpath, key_tuple, value_tuple, list_xpath)** - create a list item, to remove use **uncreate**
 - **uncreate(xpath, list_xpath** - delete a list element from the datastore.
 - **create_container(xpath)** - if a container is a presence container explicitly create the container.
 - **set(xpath, value, valuetype)** - sets the value of a specific xpath (supported for yang leaves). The valuetype is an integer (defined in Types.py/DATA_ABSTRACTION_MAPPING) based on the effective type of the yang field (*based on fuzzy matching in the case of unions*).
 - **delete(xpath** - delete a value or container, this method must not be used for lists.
 - **empty()** - a dangerous option which will remove everything from the datastore.

### SCHEMA vs DATA level constraints

There are some validation and constraints that are schema level, that is they are defined in the yang model and have no dependency on the data in the datastore. ~~Schema based constraints are enforced by libyang without a requirement to run a full datastore (like sysrepo).~~ Note: sysrepo actually calls libyang to perform the validation with the full dataset.

Examples of schema based constraints.

 - Creating/accessing nodes that are not part of the YANG model.
 - Setting data that does not match they type (i.e. string, uintX, intX, boolean)


Data level constraints need to be supported by the backend datastore, and this is true of sysrepo.

 - Validating enumerations
 - Validating must and when expressions
 - Validating data matches the path of a leafref.



## Example Docker instance

See below for for instructions setting up without docker.

The following (amd64) docker image can be used `docker pull allena29/yabgvoodoo:devel`

```bash
git pull allena29/yangvoodoo:devel
docker run -i  -t allena29/yangvoodoo:devel /bin/bash

# inside docker container
cd /working
git pull
sysrepod -d -l 2
sysrepo-plugind

## Install YANG & Initialise startup configuration

cd /working/yang
./install-yang.sh
cd /working/init-data
./init-xml.sh
```

The `./launch-dbg` script in this repository will build a docker image (*first time will be slower*) mounts the current directory (i.e. this repository) as `/working` and then runs `/working-start-in-docker.sh`. This gives a quick way of getting a fresh docker instace (after the first build - which will terminate at the end). This will launch into an interactive python session (CTRL+D) to exit to bash.


# Tests

- **unitcore** Unit tests (against stub) for voodoo node based access
- **unit** Unit tests (against stub) for extended test cases
- **integration** Integration tests (against sysrepo)
- In addition to tests *pycodestyle* and *xenon* are used for linting and complexity checks.


All tests can be executed with

```bash
./run-tests.sh
```

Integration tests can be skipped with

```bash
./run-tests.sh unit
```



# Sysrepo Datastore


See [Details Sysrepo Documentation](Documentation/Datastores.md)


# Object based python access

This is a proof of concept style quality of code at this stage.

- We allow libyang to constrain our schema, however this means some things will be **invalid** but not fail basic schema checks which libyang gives us as part of it's validations.
- Then `session.commit()` which wraps around sysrepo's commit will actually validate things like must, whens and leaf-ref pathss.


When running `get_node(yang_module)` the directory `yang` will be used to find the respective yang modules. There is a 1:1 mapping between a root object and yang module - this fits with the pattern of sysrepo. An optional argument `yang_location=<>` can be passed to get_node to specify an alternative location.



```python
import yangvoodoo
session = yangvoodoo.DataAccess()
session.connect('integrationtest', yang_location='yang')
root = session.get_node()

# Set a value
root.simpleleaf = 'abc'

# Delete of a leaf
root.simpleleaf = None

# Access a leaf inside a container
print(root.morecomplex.leaf3)
# or
print(root.morecomplex['leaf3'])

# Create (or return) a list element - this list has two boolean keys
listelement = root.twokeylist.create(True, True)
listelement.tertiary = True

# Access data with square brackets (both these two options are equivalent)
listelement = root.twokeylist[True, True]
listelement = root.twokeylist.get(True, True)

# Iterate around a list
for y in root.twokeylist:
    print("Object Representation:", repr(y))
    print("Leaf from listelement:", y.primary)
    print("Children of listelement:", dir(y))

# Delete list times
del root.twokeylist[True, True]

# Multiple levels
root.bronze.silver.gold.platinum.deep = 'abc'

# Accessing parents (this is root.bronze (use with care - it's intended for interactive debug)
root.bronze.silver._parent

# Get helptext from the YANG node, there are two formats depending on how the data is represnted.
session.decsribe(root.bronze)
session.describe(root,'simpleleaf')

# Return the argument of the extnesion 'info' if it exists on teh child node dirty_secret (otherwise None)
root.get_exension('info', 'dirty_secret')

# A special method on lists allows us to retrieve items sorted by XPATH
# instead of by the order they were added to the datastore.

for gig in root.web.bands['Yuck'].gigs._xpath_sorted:
   print(gig.year, gig.month, gig.day, gig.venue, gig.location)
   # Results in
   #  2010 10 14 Harley Sheffield
   #  2010 10 27 Lexington Islington
   #  2011 11 24 Electric Ballroom Camden
   #  2011 5 18 Scala Kings Cross

# Validate data with the sysrepo backend datastore.
session.validate()

# Refresh data from the sysrepo backend datastore.
session.refresh()
session.commit()
session.disconnect()
```


#### Session to YANG

A session maps exactly to one YANG module (including it's child nodes), in terms of the datastore we expect it will manage each module as a separate transactional boundary.

The `SuperRoot` object provides a container for multiple top-level nodes from YANG modules, the transactional boundary remains with the resepective sessions.

```python
import yangvoodoo
root = yangvoodoo.DataAccess.get_root()

session1 = yangvoodoo.DataAccess()
session1.connect("integrationtest")
session2 = yangvoodoo.DataAccess()
session2.connect("secondmodule")

root.attach_node_from_session(session1, 'morecomplex')
root.attach_node_from_session(session1, 'web')
root.attach_node_from_session(session2, 'second')
dir(root)
```


#### Templates

It is possible to apply templates to set data instead of manually setting every element of data individually. [Jinja2](http://jinja.pocoo.org/docs/2.10/) is used to provide the ability to make templates less static.

It is important to note the template is rendered **first** with the existing data, and then applied. The implication of this is that even though we set `root.simpleleaf` to `HELLO WOLRD` as the second line in the template - when we substitute the value in the 14th line will take the existing value at the time of rendering the template.


```xml
<integrationtest>
  <simpleleaf>HELLO WORLD</simpleleaf>
  <morecomplex>
    <leaf2>True</leaf2>
  </morecomplex>
  <simplelist>
    <simplekey>KEY</simplekey>
    <nonleafkey>NONKEY</nonleafkey>
  </simplelist>
  <bronze>
    <silver>
      <gold>
        <platinum>
          <deep>{{ root.simpleleaf }}</deep>
        </platinum>
      </gold>
    </silver>
  </bronze>
</integrationtest>
```

```python
root.simpleleaf='Before Value'
root.from_template('templates/sample.xml')
```


#### Using a stub and writing unit tests

When writing unit tests it is expensive to make use of the real sysrepo backend, this projectThis is a proof of concept style quality of code at this stage. This reduces the dependencies to just libyang library and the forked libyang-cffi bindings.

```python
import unittest
import yangvoodoo
import yangvoodoo.stubdal


class test_node_based_access(unittest.TestCase):

    def setUp(self):
        self.stub = yangvoodoo.stubdal.StubDataAbstractionLayer()
        self.subject = yangvoodoo.DataAccess(data_abstraction_layer=self.stub)
        self.subject.connect('integrationtest')
        self.root = self.subject.get_node()
```




# Install

[Installing local versions](INSTALL.md)



# TODO LIST

see [TODO LIST](TODO.md)


# Reference:

- [Sysrepo](http://www.sysrepo.org/)
- [Libyang](https://github.com/CESNET/libyang)
- [libyang python bindings](https://github.com/allena29/libyang-cffi)
- [Low level C development notes](DEVEL.md)
