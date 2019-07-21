import unittest
import yangvoodoo
import yangvoodoo.stubdal


class test_stub_datastore(unittest.TestCase):

    maxDiff = 50000

    def setUp(self):
        self.maxDiff = None
        self.subject = yangvoodoo.stubdal.StubDataAbstractionLayer()

    def test_get(self):
        result = self.subject.get("/xxxx", "default")
        self.assertEqual(result, "default")

        self.subject.stub_store["/xxxx"] = "not-default"
        result = self.subject.get("/xxxx", "default")

        self.assertEqual(result, "not-default")

    def test_create(self):
        self.subject.create("/integrationtest:simplelist[simplekey='sdf']",
                            keys=('simplekey',), values=(('sdf', 10),), list_xpath="/integrationtest:simplelist")
        self.subject.create("/integrationtest:simplelist[simplekey='xyz']",
                            keys=('simplekey',), values=(('xyz', 10),),  list_xpath="/integrationtest:simplelist")
        self.subject.set("/integrationetest:simpleleaf", "ABC")
        self.subject.add("/integrationetest:morecomplex/integrationtest:leaflists/integrationtest:simple", "ABC", 10)
        self.subject.add("/integrationetest:morecomplex/integrationtest:leaflists/integrationtest:simple", "XYZ", 10)

        self.subject.set("/integrationtest:underscoretests/integrationtest:underscore_only", "A", 10)

        expected_result = {
            "/integrationtest:simplelist[simplekey='sdf']": (1, '/integrationtest:simplelist'),
            "/integrationtest:simplelist[simplekey='sdf']/simplekey": 'sdf',
            "/integrationtest:simplelist[simplekey='xyz']": (1, '/integrationtest:simplelist'),
            "/integrationtest:simplelist[simplekey='xyz']/simplekey": 'xyz',
            '/integrationetest:simpleleaf': 'ABC',
            '/integrationetest:morecomplex/integrationtest:leaflists/integrationtest:simple': ['ABC', 'XYZ'],
            '/integrationtest:underscoretests/integrationtest:underscore_only': 'A'
        }
        self.assertEqual(self.subject.stub_store, expected_result)

        expected_result = {
            '/integrationtest:simplelist': ["/integrationtest:simplelist[simplekey='sdf']",
                                            "/integrationtest:simplelist[simplekey='xyz']"]
        }
        self.assertEqual(self.subject.list_element_map, expected_result)

        self.assertEqual(list(self.subject.gets("/integrationetest:morecomplex/integrationtest:leaflists/integrationtest:simple")),
                         ['ABC', 'XYZ'])

        expected_result = ["/integrationtest:simplelist[simplekey='sdf']",
                           "/integrationtest:simplelist[simplekey='xyz']"]
        self.assertEqual(list(self.subject.gets_sorted("/integrationtest:simplelist", "/integrationtest:simplelist")), expected_result)

        self.subject.delete("/integrationtest:simplelist[simplekey='sdf']")
        self.assertEqual(len(list(self.subject.gets_unsorted('/integrationtest:simplelist', "/integrationtest:simplelist"))), 1)

        self.subject.remove("/integrationetest:morecomplex/integrationtest:leaflists/integrationtest:simple", "XYZ")

        self.subject.delete("/integrationtest:underscoretests")

        expected_result = {
            "/integrationtest:simplelist[simplekey='xyz']": (1, '/integrationtest:simplelist'),
            "/integrationtest:simplelist[simplekey='xyz']/simplekey": 'xyz',
            '/integrationetest:simpleleaf': 'ABC',
            '/integrationetest:morecomplex/integrationtest:leaflists/integrationtest:simple': ['ABC']
        }

        self.assertEqual(self.subject.stub_store, expected_result)
