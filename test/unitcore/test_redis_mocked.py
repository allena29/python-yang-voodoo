import unittest
import yangvoodoo
from mock import Mock
from yangvoodoo.redisdal import RedisDataAbstractionLayer
from yangvoodoo.Errors import UnableToLockDatastoreError, LockWasBrokenDuringTransactionError


class test_redis(unittest.TestCase):

    def setUp(self):

        self.redisstub = RedisDataAbstractionLayer()
        self.redisstub.connect = Mock()
        self.redisstub.redis = Mock()
        self.redisstub.id = "mocked-redis"

        self.session = yangvoodoo.DataAccess(data_abstraction_layer=self.redisstub, disable_proxy=True)
        self.session.connect('integrationtest')
        self.root = self.session.get_node()
        self.session.empty()

    def test_release_lock(self):
        # Build
        self.redisstub.id = 'uuid-id'
        self.redisstub.redis = Mock()
        self.redisstub.redis.get.return_value = 'uuid-id'.encode('utf-8')

        # Act
        result = self.redisstub._release_lock()

        # Assert
        self.redisstub.redis.delete.assert_called_once_with("/internal/transaction-lock")
        self.assertTrue(result)

    def test_release_lock_when_broken(self):
        # Build
        self.redisstub.id = 'uuid-id'
        self.redisstub.redis = Mock()
        self.redisstub.redis.get.return_value = 'some-other-uuid'.encode('utf-8')

        # Act
        with self.assertRaises(yangvoodoo.Errors.LockWasBrokenDuringTransactionError) as context:
            self.redisstub._release_lock()

        # Assert
        self.assertEqual(str(context.exception), "Unable to unlock the datastore.\nLocked broken by some-other-uuid")

    def test_get_lock(self):
        # Build
        self.redisstub.id = 'uuid-id'
        self.redisstub.redis = Mock()

        # Act
        result = self.redisstub._get_lock(wait=2, interval=0.0001)

        # Assert
        self.redisstub.redis.setnx.assert_called_once_with("/internal/transaction-lock", 'uuid-id')
        self.assertTrue(result)

    def test_get_lock_fails(self):
        # Build
        self.redisstub.id = 'uuid-id'
        self.redisstub.redis = Mock()
        self.redisstub.redis.setnx.return_value = False
        self.redisstub.redis.get.return_value = "other"

        # Act
        with self.assertRaises(UnableToLockDatastoreError) as context:
            self.redisstub._get_lock(wait=2, interval=0.0001)

        # Assert
        self.assertEqual(str(context.exception), "Unable to lock the datastore to commit our changes.\nLocked by other")

    def test_leaf(self):
        # Build
        self.redisstub._get_lock = Mock()
        self.redisstub._release_lock = Mock()
        self.redisstub.redis.get.side_effect = [
            None,
            None,
            "hello".encode('utf-8'),
            "world".encode('utf-8')
        ]

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
