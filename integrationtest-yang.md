# YANG Structure for testing.

```
module: integrationtest
  +--rw imports-in-here
  |  +--rw name?   string
  +--rw web
  |  +--rw venues* [name location]
  |  |  +--rw name           string
  |  |  +--rw location       locations
  |  |  +--rw country?       countries
  |  |  +--rw beers* [name]
  |  |  |  +--rw name    string
  |  |  +--rw information
  |  |     +--rw profiles* [profile]
  |  |        +--rw profile       string
  |  |        +--rw doors-open?   string
  |  |        +--rw curfew?       string
  |  +--rw promoters* [name]
  |  |  +--rw name    string
  |  +--rw bands* [name]
  |  |  +--rw name    string
  |  |  +--rw gigs* [year month day venue location]
  |  |     +--rw year        uint16
  |  |     +--rw month       uint8
  |  |     +--rw day         uint8
  |  |     +--rw venue       -> /web/venues/name
  |  |     +--rw location    -> /web/venues[integrationtest:name=current()/../venue]/location
  |  |     +--rw festival?   string
  |  |     +--rw missed!
  |  |     |  +--rw reason?   string
  |  |     +--rw comments?   string
  |  |     +--rw rating?     uint8
  |  |     +--rw support* [name]
  |  |        +--rw name     -> /web/bands/name
  |  |        +--rw order?   enumeration
  |  +--rw favourite?   -> ../bands/name
  +--rw underscoretests
  |  +--rw underscore_only?         string
  |  +--rw hyphen-only?             string
  |  +--rw underscore_and-hyphen?   string
  +--rw empty?                                empty
  +--rw simpleleaf?                           string
  +--rw dirty-secret?                         string
  +--rw default?                              string
  +--rw whencontainer
  |  +--rw then?   string
  +--rw thing-that-is-lit-up-for-C?           string
  +--rw thing-that-is-lit-up-for-B?           string
  +--rw thing-that-is-lit-up-for-A?           string
  +--rw thing-that-is-used-for-when?          enumeration
  +--rw thing-to-leafref-against?             string
  +--rw list-to-leafref-against* [idle]
  |  +--rw idle    string
  |  +--rw wild?   string
  +--rw thing-that-is-a-list-based-leafref?   -> ../list-to-leafref-against/wild
  +--rw thing-that-is-leafref?                -> ../thing-to-leafref-against
  +--rw quad
  |  +--rw leafinquad!
  +--rw quarter
  |  +--rw leafinquarter!
  +--rw bronze
  |  +--rw silver
  |     +--rw gold
  |        +--rw platinum
  |           +--rw deep?   string
  +--rw psychedelia
  |  +--rw bands* [band]
  |  |  +--rw band         string
  |  |  +--rw favourite?   boolean
  |  +--rw psychedelic-rock
  |     +--rw bands* [band]
  |     |  +--rw band         string
  |     |  +--rw favourite?   boolean
  |     +--rw stoner-rock
  |     |  +--rw bands* [band]
  |     |     +--rw band         string
  |     |     +--rw favourite?   boolean
  |     |     +--rw albums* [album]
  |     |        +--rw album    string
  |     +--rw noise-pop
  |        +--rw bands* [band]
  |        |  +--rw band         string
  |        |  +--rw favourite?   boolean
  |        +--rw dream-pop
  |        |  +--rw bands* [band]
  |        |     +--rw band         string
  |        |     +--rw favourite?   boolean
  |        +--rw shoe-gaze
  |           +--rw bands* [band]
  |              +--rw band         string
  |              +--rw favourite?   boolean
  +--rw twokeylist* [primary secondary]
  |  +--rw primary      boolean
  |  +--rw secondary    boolean
  |  +--rw tertiary?    boolean
  +--rw simplecontainer!
  +--rw simpleenum?                           enumeration
  +--rw patternstr?                           string
  +--rw hyphen-leaf?                          string
  +--rw outsidelist* [leafo]
  |  +--rw leafo              string
  |  +--rw insidelist* [leafi]
  |  |  +--rw leafi    string
  |  +--rw otherinsidelist* [otherlist1 otherlist2 otherlist3]
  |  |  +--rw otherlist1    string
  |  |  +--rw otherlist2    string
  |  |  +--rw otherlist3    string
  |  |  +--rw otherlist4?   string
  |  |  +--rw otherlist5?   string
  |  |  +--rw language?     enumeration
  |  +--rw other?             string
  +--rw numberlist
  |  +--rw integer* [k]
  |  |  +--rw k    uint8
  |  +--rw fraction* [k]
  |  |  +--rw k    testchild:temperature
  |  +--rw percentage* [k]
  |     +--rw k    testchild:percent-dot1
  +--rw container-and-lists
  |  +--rw just-a-key?       string
  |  +--rw multi-key-list* [A B]
  |  |  +--rw A        string
  |  |  +--rw B        string
  |  |  +--rw inner
  |  |     +--rw C?   string
  |  +--rw numberkey-list* [numberkey]
  |     +--rw numberkey      uint8
  |     +--rw description?   string
  +--rw lista* [firstkey]
  |  +--rw firstkey    string
  |  +--rw listb* [secondkey thirdkey]
  |     +--rw secondkey             string
  |     +--rw thirdkey              string
  |     +--rw nonkey?               string
  |     +--rw (MAKEYOURMINDUP)?
  |     |  +--:(OPTION1)
  |     |  |  +--rw FIRSTOPTION?    string
  |     |  +--:(OPTION2)
  |     |     +--rw SECONDOPTION?   string
  |     +--rw things
  |     |  +--rw thing?      string
  |     |  +--rw musthave    string
  |     +--rw nothings
  +--rw simplelist* [simplekey]
  |  +--rw simplekey     string
  |  +--rw nonleafkey?   uint32
  +--rw resolver
  |  +--rw a?        string
  |  +--rw leaf-a?   type-a
  +--rw morecomplex
     +--rw superstar?       percentile95th
     +--rw percentage?      decimal64
     +--ro nonconfig?       string
     +--rw extraboolean?    boolean
     +--rw extraboolean2?   boolean
     +--rw extraboolean3?   boolean
     +--rw leaf2?           boolean
     +--rw leaf3?           type2
     +--rw leaf4?           type4
     +--rw inner!
        +--rw list-that-will-stay-empty* [akey]
        |  +--rw akey    string
        +--rw leaf5                        string
        +--rw leaf6?                       string
        +--rw leaf7?                       string
        +--rw leaf8?                       type8
        +--rw leaf666?                     type6
        +--rw leaf777?                     -> ../leaf7
        +--rw leaf888?                     -> ../leaf666
        +--rw leaf999?                     -> ../../leaf2
        +--rw leaf000?                     sillytypedef
        +--rw ietf-inet-types
           +--rw ip
              +--rw address?   inet:ip-address
```
