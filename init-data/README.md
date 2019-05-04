# Importing Data

Data can be imported by providing XML fragments in this directory, and will automatically be included when launching docker.

The `init-xml.sh` script can be run with an optional `running` parameter to push data to the running datastore rather than the default startup datastore.

### Naming Conventions

The file name must begin with the prefix from the YANG module with an .xml prefix e.g. `integrationtest.xml`.
To help split large datasets the additional files can be provided with a suffix after the module name `integrationtest__extra.xml`.

Files without any suffix will be imported (data for the module replaced), files with a suffix will be merged.


### Example XML

The XML fragments must refrence the namespace of the YANG module.

```xml
<simpleleaf xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">duke</simpleleaf>
```



### Invalid Merges

libyang/sysrepo does not like the same container twice in the same document.

`sysrepocfg: /opt/dev/libyang/src/tree_data.c:3393: lyd_diff_match: Assertion `!(first->validity & LYD_VAL_INUSE)' failed.`


```xml
<web xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
    ....
</web>
<web xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
    ....
</web>
```


Further more if we spit this into two subfiles we may not successfully manage to merge these in if there are leafref dependencies that File2 requires from File1.

##### File 1

```xml
<web xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
    ....
</web>
```

##### File 2

```xml
<web xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">
    ....
</web>
```
