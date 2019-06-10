import unittest
import yangvoodoo
import yangvoodoo.stubdal


"""
This set of unit tests uses the stub backend datastore, which is not preseeded with
any data.
"""


class test_node_based_access(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.stub = yangvoodoo.stubdal.StubDataAbstractionLayer()
        self.subject = yangvoodoo.DataAccess(data_abstraction_layer=self.stub)
        self.subject.connect('integrationtest')
        self.root = self.subject.get_node()

    def test_root(self):
        self.assertEqual(repr(self.root), 'VoodooNodeRoot{} YANG Module: integrationtest')

        expected_children = ['bronze', 'cli', 'container_and_lists', 'default', 'diff', 'dirty_secret', 'empty',
                             'hyphen_leaf', 'imports_in_here', 'list_to_leafref_against', 'lista', 'morecomplex',
                             'numberlist', 'outsidelist', 'patternstr', 'psychedelia', 'quad', 'quarter',
                             'resolver', 'simplecontainer', 'simpleenum', 'simpleleaf', 'simplelist',
                             'thing_that_is_a_list_based_leafref', 'thing_that_is_leafref',
                             'thing_that_is_lit_up_for_A', 'thing_that_is_lit_up_for_B', 'thing_that_is_lit_up_for_C',
                             'thing_that_is_used_for_when', 'thing_to_leafref_against', 'twokeylist', 'underscore_and_hyphen',
                             'underscoretests', 'validator', 'web', 'whencontainer']

        self.assertEqual(dir(self.root), expected_children)

    def test_simplest_leaf(self):
        self.root.simpleleaf = 'spirit'
        self.assertEqual(self.root.simpleleaf, 'spirit')

        self.root.simpleleaf = None
        self.assertEqual(self.root.simpleleaf, None)

        result = self.root.default
        self.assertEqual(result, "statusquo")

        self.subject.commit()

        self.root.simpleenum = 'A'

        with self.assertRaises(yangvoodoo.Errors.ValueDoesMatchEnumeration) as context:
            self.root.simpleenum = 'Z'
        self.assertEqual(str(context.exception), "The value Z is not valid for the enumeration at path /integrationtest:simpleenum")

        self.assertFalse(self.root.empty.exists())
        self.root.empty.create()
        self.assertEqual(repr(self.root.empty), "VoodooEmpty{/integrationtest:empty} - Exists")
        self.assertTrue(self.root.empty.exists())
        self.root.empty.remove()
        self.assertEqual(repr(self.root.empty), "VoodooEmpty{/integrationtest:empty} - Does Not Exist")
        self.assertFalse(self.root.empty.exists())

    def test_containers(self):
        morecomplex = self.root.morecomplex
        self.assertEqual(repr(morecomplex), "VoodooContainer{/integrationtest:morecomplex}")

        expected_children = ['extraboolean', 'extraboolean2', 'extraboolean3', 'inner', 'leaf2', 'leaf3', 'leaf4',
                             'leaflists', 'nonconfig', 'percentage', 'superstar']
        self.assertEqual(dir(morecomplex), expected_children)

        inner = morecomplex.inner.create()
        self.assertEqual(repr(inner),
                         'VoodooPresenceContainer{/integrationtest:morecomplex/inner} Exists')
        inner.leaf7 = 'this-is-not-a-default-now'
        self.assertEqual(morecomplex.inner.leaf7, 'this-is-not-a-default-now')
        self.assertTrue(morecomplex.inner.exists())

        simplecontainer = self.root.simplecontainer
        self.assertEqual(repr(simplecontainer),
                         "VoodooPresenceContainer{/integrationtest:simplecontainer} Does Not Exist")
        self.assertFalse(simplecontainer.exists())

        simplecontainer.create()
        self.assertTrue(simplecontainer.exists())

        self.assertEqual(repr(self.root.morecomplex['inner']), "VoodooPresenceContainer{/integrationtest:morecomplex/inner} Exists")

    def test_list(self):
        # Build
        self.root.twokeylist.create(True, False).tertiary = True
        self.root.twokeylist.create(True, True).tertiary = True

        # Act
        twolist = self.root.twokeylist
        self.assertEqual(repr(twolist), "VoodooList{/integrationtest:twokeylist}")
        self.assertEqual(twolist._path, '/integrationtest:twokeylist')

        with self.assertRaises(yangvoodoo.Errors.ListWrongNumberOfKeys) as context:
            twolist.get('true')
        self.assertEqual(str(context.exception),
                         'The path: /integrationtest:twokeylist is a list requiring 2 keys but was given 1 keys')

        listelement = twolist.get(True, False)
        expected_children = ['primary', 'secondary', 'tertiary']
        self.assertEqual(repr(listelement),
                         "VoodooListElement{/integrationtest:twokeylist[primary='true'][secondary='false']}")
        self.assertEqual(dir(listelement), expected_children)
        self.assertEqual(listelement.tertiary, True)

        listelement.tertiary = False
        self.assertEqual(listelement.tertiary, False)

        listelement = twolist.get(True, True)
        expected_children = ['primary', 'secondary', 'tertiary']
        self.assertEqual(repr(listelement),
                         "VoodooListElement{/integrationtest:twokeylist[primary='true'][secondary='true']}")
        self.assertEqual(dir(listelement), expected_children)
        self.assertEqual(listelement.tertiary, True)

    def test_iteration_of_lists(self):
        # Build
        self.root.psychedelia.psychedelic_rock.stoner_rock.bands.create('Dead Meadow')
        self.root.psychedelia.psychedelic_rock.stoner_rock.bands.create('Wooden Shjips')
        self.root.twokeylist.create(True, True)

        # Act.
        expected_answers = [
            "VoodooListElement{/integrationtest:psychedelia/psychedelic-rock/stoner-rock/bands[band='Dead Meadow']}",
            "VoodooListElement{/integrationtest:psychedelia/psychedelic-rock/stoner-rock/bands[band='Wooden Shjips']}"
        ]
        for band in self.root.psychedelia.psychedelic_rock.stoner_rock.bands:
            expected_answer = expected_answers.pop(0)
            self.assertEqual(repr(band), expected_answer)

        self.assertTrue("Dead Meadow" in self.root.psychedelia.psychedelic_rock.stoner_rock.bands)
        self.assertFalse("Taylor Swift" in self.root.psychedelia.psychedelic_rock.stoner_rock.bands)

        twolist = self.root.twokeylist
        self.assertTrue((True, True) in twolist)

        other_list = self.root.container_and_lists.multi_key_list
        self.assertEqual(repr(other_list), "VoodooList{/integrationtest:container-and-lists/multi-key-list}")
        self.assertFalse(('A', 'Z') in other_list)

        item = other_list.create('A', 'Z')
        self.assertTrue(('A', 'Z') in other_list)

        # Test __getitem__
        self.assertEqual(repr(item), "VoodooListElement{/integrationtest:container-and-lists/multi-key-list[A='A'][B='Z']}")
        #
        # # Test delete item
        self.assertEqual(len(other_list), 1)
        other_list.create('thing', 'todelete').inner.C = 'soon'
        self.assertEqual(len(other_list), 2)
        self.assertEqual(other_list['thing', 'todelete'].inner.C, 'soon')

        del other_list['thing', 'todelete']
        self.assertEqual(len(other_list), 1)

        number_list = self.root.container_and_lists.numberkey_list
        element = number_list.create(3)
        number_list.create(4)
        self.assertEqual(repr(element),
                         "VoodooListElement{/integrationtest:container-and-lists/numberkey-list[numberkey='3']}")
        element = number_list.get(4)
        self.assertEqual(repr(element),
                         "VoodooListElement{/integrationtest:container-and-lists/numberkey-list[numberkey='4']}")
        element = number_list.get(3)
        self.assertEqual(repr(element),
                         "VoodooListElement{/integrationtest:container-and-lists/numberkey-list[numberkey='3']}")

        for x in self.root.morecomplex.inner.list_that_will_stay_empty:
            self.fail('Did not expect any data in the list')

        self.assertEqual(len(self.root.morecomplex.inner.list_that_will_stay_empty), 0)

        self.assertFalse('x' in self.root.morecomplex.inner.list_that_will_stay_empty)

    def test_decimal64_and_typedef_resolving(self):
        self.root.morecomplex.superstar = 95.6
        self.assertEqual(int(self.root.morecomplex.superstar * 100), 9560)

    def test_parents_and_help_text(self):
        great_grandparent = self.root.bronze.silver.gold.platinum._parent._parent._parent

        self.assertEqual(repr(great_grandparent), "VoodooContainer{/integrationtest:bronze}")

        description = self.subject.describe(great_grandparent, print_description=False)

        expected_description = """Description of bronze
---------------------

Schema Path: /integrationtest:bronze
Value Path: /integrationtest:bronze
NodeType: Container

Description:
  The metallics are used to test container nesting

Children: 'silver'"""

        self.assertEqual(description, expected_description)

        list_element = self.root.simplelist.create('newlistitem')
        self.assertEqual(repr(list_element._parent), "VoodooList{/integrationtest:simplelist}")

        obj = self.root.bronze.silver._parent.silver._parent.silver.gold
        self.assertEqual(repr(obj),
                         "VoodooContainer{/integrationtest:bronze/silver/gold}")

    def test_lists_ordering(self):
        self.root.simplelist.create('A')
        self.root.simplelist.create('Z')
        self.root.simplelist.create('middle')
        self.root.simplelist.create('M')

        # GETS is based on user defined order
        # Act
        items = list(self.root.simplelist)
        # Assert
        expected_results = ["VoodooListElement{/integrationtest:simplelist[simplekey='A']}",
                            "VoodooListElement{/integrationtest:simplelist[simplekey='Z']}",
                            "VoodooListElement{/integrationtest:simplelist[simplekey='middle']}",
                            "VoodooListElement{/integrationtest:simplelist[simplekey='M']}"]

        for i in range(len(items)):
            self.assertEqual(repr(items[i]), expected_results[i])

        expected_result = ["/integrationtest:simplelist[simplekey='A']",
                           "/integrationtest:simplelist[simplekey='Z']",
                           "/integrationtest:simplelist[simplekey='middle']",
                           "/integrationtest:simplelist[simplekey='M']"]
        self.assertEqual(list(self.root.simplelist.elements()), expected_result)

        # GETS_SORTED is based on xpath sorted order
        # Act
        items = list(self.root.simplelist._xpath_sorted)

        # Assert
        expected_results = ["VoodooListElement{/integrationtest:simplelist[simplekey='A']}",
                            "VoodooListElement{/integrationtest:simplelist[simplekey='M']}",
                            "VoodooListElement{/integrationtest:simplelist[simplekey='Z']}",
                            "VoodooListElement{/integrationtest:simplelist[simplekey='middle']}"]

        for i in range(len(items)):
            self.assertEqual(repr(items[i]), expected_results[i])

        outside_a = self.root.outsidelist.create('a')
        outside_a.insidelist.create('1')
        outside_a.insidelist.create('2')
        outside_b = self.root.outsidelist.create('b')
        outside_b.insidelist.create('3')
        self.assertEqual(len(outside_a.insidelist), 2)
        self.assertEqual(len(outside_b.insidelist), 1)

    def test_super_root(self):
        session1 = yangvoodoo.DataAccess(data_abstraction_layer=self.stub)
        session1.connect('integrationtest')

        session2 = yangvoodoo.DataAccess(data_abstraction_layer=self.stub)
        session2.connect('integrationtest')

        super_root = yangvoodoo.DataAccess.get_root(session1, 'web')
        super_root.attach_node_from_session(session2, 'morecomplex')

        self.assertEqual(dir(super_root), ['morecomplex', 'web'])
        self.assertEqual(repr(super_root.morecomplex), 'VoodooContainer{/integrationtest:morecomplex}')
        self.assertEqual(repr(super_root.web), 'VoodooContainer{/integrationtest:web}')

    def test_leaf_lists(self):
        self.assertEqual(repr(self.root.morecomplex.leaflists.simple),
                         "VoodooLeafList{/integrationtest:morecomplex/leaflists/simple}")

        ll = self.root.morecomplex.leaflists.simple
        ll.create('A')
        ll.create('Z')
        ll.create('B')

        expected_result = {
            '/integrationtest:morecomplex/leaflists/simple': ['A', 'Z', 'B']
        }

        self.assertEqual(expected_result, self.stub.stub_store)

        expected = ['A', 'Z', 'B']
        received = []
        for x in self.root.morecomplex.leaflists.simple:
            received.append(x)
        self.assertEqual(received, expected)

        self.assertEqual(3, len(self.root.morecomplex.leaflists.simple))

        self.assertFalse('non-existant' in self.root.morecomplex.leaflists.simple)
        self.assertTrue('A' in self.root.morecomplex.leaflists.simple)

        del self.root.morecomplex.leaflists.simple['A']

        self.assertEqual(2, len(self.root.morecomplex.leaflists.simple))
        self.assertFalse('A' in self.root.morecomplex.leaflists.simple)

    def test_extensions(self):
        expected_result = [('crux:hide', True)]
        self.assertEqual(expected_result, list(yangvoodoo.DataAccess.get_extensions(self.root, 'dirty-secret')))

        expected_result = [('integrationtest:hide', True)]
        self.assertEqual(expected_result, list(yangvoodoo.DataAccess.get_extensions(self.root, 'default')))

        expected_result = []
        self.assertEqual(expected_result, list(yangvoodoo.DataAccess.get_extensions(self.root, 'default', module='crux')))

        expected_result = "underscores help text for the container"
        self.assertEqual(expected_result, yangvoodoo.DataAccess.get_extension(self.root.underscoretests, 'info'))

        expected_result = "underscores help text"
        self.assertEqual(expected_result, yangvoodoo.DataAccess.get_extension(self.root.underscoretests, 'info', 'underscore_only'))

    def test_choices(self):
        self.assertEqual(repr(self.root.morecomplex.inner.beer_type), "VoodooChoice{/integrationtest:morecomplex/inner/...beer-type}")
        self.assertEqual(repr(self.root.morecomplex.inner.beer_type.craft), "VoodooCase{/integrationtest:morecomplex/inner/...craft}")

        self.root.morecomplex.inner.beer_type.craft.brewdog = "PUNK IPA"
        self.assertEqual(self.root.morecomplex.inner.beer_type.craft.brewdog, "PUNK IPA")
        self.assertEqual(self.stub.stub_store['/integrationtest:morecomplex/inner/brewdog'], 'PUNK IPA')

    def test_silly_things(self):
        with self.assertRaises(yangvoodoo.Errors.CannotAssignValueToContainingNode) as context:
            self.root.morecomplex = 'ssdfsdf'
        self.assertEqual(str(context.exception), "Cannot assign a value to morecomplex")
        self.assertNotEqual(self.root.morecomplex.inner.beer_type.craft.brewdog, "PUNK IPA")

    def test_underscore_and_hyphens(self):
        self.root.underscoretests.underscore_and_hyphen = 'sdf'
        self.root.underscore_and_hyphen.create()
        self.assertEqual(self.root.underscoretests.underscore_and_hyphen, "sdf")
        self.assertEqual(repr(self.root.underscore_and_hyphen), "VoodooEmpty{/integrationtest:underscore_and-hyphen} - Exists")
        xpaths = self.stub.dump_xpaths()
        self.assertEqual(xpaths["/integrationtest:underscoretests/underscore_and-hyphen"], "sdf")
        self.assertEqual(xpaths["/integrationtest:underscore_and-hyphen"], True)
