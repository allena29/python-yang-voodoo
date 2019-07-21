import unittest
import yangvoodoo
from yangvoodoo.redisdal import RedisDataAbstractionLayer


class test_redis(unittest.TestCase):

    def setUp(self):

        self.redisstub = RedisDataAbstractionLayer()
        self.session = yangvoodoo.DataAccess(data_abstraction_layer=self.redisstub, disable_proxy=True)
        self.session.connect('integrationtest')
        self.root = self.session.get_node()
        self.session.empty()
        self.dal = self.session.data_abstraction_layer

    def test_lists(self):
        xpath = "/integrationtest:simplelist"
        self.session.create("/integrationtest:simplelist[simplekey='A']",
                            keys=['simplekey'], values=[('A', 18)], list_xpath="/integrationtest:simplelist")
        self.session.create("/integrationtest:simplelist[simplekey='B']",
                            keys=['simplekey'], values=[('B', 18)], list_xpath="/integrationtest:simplelist")
        self.session.create("/integrationtest:simplelist[simplekey='C']",
                            keys=['simplekey'], values=[('B', 18)], list_xpath="/integrationtest:simplelist")

        self.assertEqual(self.dal.paths_list_set["metadata-listkey" + xpath],
                         ["data/integrationtest:simplelist[simplekey='A']",
                          "data/integrationtest:simplelist[simplekey='B']",
                          "data/integrationtest:simplelist[simplekey='C']"])

        self.session.uncreate("/integrationtest:simplelist[simplekey='C']", list_xpath="/integrationtest:simplelist")

        self.assertEqual(self.dal.paths_list_set["metadata-listkey" + xpath],
                         ["data/integrationtest:simplelist[simplekey='A']",
                          "data/integrationtest:simplelist[simplekey='B']"])

        self.session.commit()

        self.assertEqual(self.dal.paths_list_set, {})

        self.session.uncreate("/integrationtest:simplelist[simplekey='B']", list_xpath="/integrationtest:simplelist")

        self.assertEqual(self.dal.paths_list_removed["metadata-listkey" + xpath],
                         ["data/integrationtest:simplelist[simplekey='B']"])

    def test_presence_containers(self):
        xpath = "/integrationtest:container1"
        self.session.create_container(xpath)
        self.assertTrue(self.session.container(xpath))
        self.assertEqual(self.dal.paths_set["data" + xpath], '__container')
        self.session.commit()

        self.assertEqual(self.dal.paths_set, {})
        self.assertTrue(self.session.container(xpath))

        self.assertFalse(self.session.container(xpath+"_nonexistant"))

    def test_leaflists(self):
        xpath = "/integrationtest:morecomplex/leaflists/simple"
        result = self.session.add(xpath, "A")
        result = self.session.add(xpath, "BX")
        self.assertEqual(self.dal.paths_leaflist_set["data" + xpath], ['A', 'BX'])
        self.session.commit()

        result = self.session.remove(xpath, "BX")
        result = self.session.add(xpath, "B")
        result = self.session.add(xpath, "C")
        result = self.session.add(xpath, "D")
        self.assertEqual(self.dal.paths_leaflist_set["data" + xpath], ['B', 'C', 'D'])
        self.assertEqual(self.dal.paths_leaflist_removed["data" + xpath], ['BX'])
        self.session.commit()

        self.assertEqual(self.dal.paths_leaflist_set, {})
        self.assertEqual(self.dal.paths_leaflist_removed, {})

        result = self.session.gets(xpath)
        self.assertEqual(result, ["A", "B", "C", "D"])

    def test_leaf(self):
        xpath = "/integrationtest:simpleleaf"
        result = self.session.get(xpath)
        self.assertEqual(result, None)

        result_with_default = self.session.get(xpath, "default")
        self.assertEqual(result_with_default, "default")

        result = self.session.set(xpath, "hello")
        self.assertEqual(result, True)
        self.assertEqual(self.dal.paths_set, {"data"+xpath: 'hello'})

        self.assertEqual("hello", self.root.simpleleaf)

        result = self.session.delete(xpath)
        self.assertEqual(result, True)
        self.assertTrue("data"+xpath in self.dal.paths_removed)
        self.assertFalse("data"+xpath in self.dal.paths_set)

        result = self.session.set(xpath, "world")
        self.assertEqual(result, True)
        self.assertEqual(self.dal.paths_set, {"data"+xpath: 'world'})
        self.assertFalse("data"+xpath in self.dal.paths_removed)

        result = self.session.commit()
        self.assertTrue(result)

        self.assertFalse("data"+xpath in self.dal.paths_set)
        self.assertFalse("data"+xpath in self.dal.paths_removed)

        result = self.session.get(xpath)
        self.assertEqual(result, 'world')
