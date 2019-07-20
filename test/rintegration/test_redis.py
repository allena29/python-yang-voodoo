import unittest
import yangvoodoo
from mock import Mock
from yangvoodoo.redisdal import RedisDataAbstractionLayer
from yangvoodoo.Errors import UnableToLockDatastoreError, LockWasBrokenDuringTransactionError


class test_redis(unittest.TestCase):

    def setUp(self):

        self.redisstub = RedisDataAbstractionLayer()
        self.session = yangvoodoo.DataAccess(data_abstraction_layer=self.redisstub, disable_proxy=True)
        self.session.connect('integrationtest')
        self.root = self.session.get_node()
        self.session.empty()

    def test_leaf(self):
        xpath = "/integrationtest:simpleleaf"
        result = self.session.get(xpath)
        self.assertEqual(result, None)

        result_with_default = self.session.get(xpath, "default")
        self.assertEqual(result_with_default, "default")

        result = self.session.set(xpath, "hello")
        self.assertEqual(result, True)
        self.assertEqual(self.session.data_abstraction_layer.paths_set, {xpath: 'hello'})

        self.assertEqual("hello", self.root.simpleleaf)

        result = self.session.delete(xpath)
        self.assertEqual(result, True)
        self.assertTrue(xpath in self.session.data_abstraction_layer.paths_removed)

        result = self.session.set(xpath, "world")
        self.assertEqual(result, True)
        self.assertEqual(self.session.data_abstraction_layer.paths_set, {xpath: 'world'})
        self.assertFalse(xpath in self.session.data_abstraction_layer.paths_removed)

        result = self.session.commit()
        self.assertTrue(result)

        self.assertFalse(xpath in self.session.data_abstraction_layer.paths_set)
        self.assertFalse(xpath in self.session.data_abstraction_layer.paths_removed)

        result = self.session.get(xpath)
        self.assertEqual(result, 'world')
