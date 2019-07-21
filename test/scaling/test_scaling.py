import unittest
import yangvoodoo
from yangvoodoo.TemplateNinja import TemplateNinja
import yangvoodoo.stubdal
import yangvoodoo.redisdal

import time


class test_nested_list_stuff(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None
        self.stub = yangvoodoo.stubdal.StubDataAbstractionLayer()
        self.redis = yangvoodoo.redisdal.RedisDataAbstractionLayer()

        self.session = yangvoodoo.DataAccess(data_abstraction_layer=self.redis, disable_proxy=True)
    #    self.session = yangvoodoo.DataAccess(data_abstraction_layer=self.stub, disable_proxy=True)
        self.session.connect('integrationtest')
        self.root = self.session.get_node()
        self.template_ninja = TemplateNinja()

    def assertExecutionTime(self, start_time, end_time, limit, threshold=0.75):
        if end_time - start_time > limit:
            self.fail("Execution time: %s wanted less than %s" % (end_time-start_time, limit))
        if (end_time - start_time) < limit * threshold:
            self.fail("TOO GOOD TO BE TRUE.. execution was %s%% of expeciton (actual: %s, execpted: %s)" % (threshold,
                                                                                                            end_time-start_time, limit))

    def test_add_one_entry_to_thirty_nested_lists(self):
        """
        This test is against sysrepo datastore, when we proxy read/requests from the proxy data store.
        """
        start_time = time.time()
        this_node = self.root.scaling
        for c in range(30):
            if c == 2:
                key = ('created%s' % (c), 'extrakey')
            else:
                key = ('created%s' % (c))
            this_node = this_node['scale%s' % (c)].create(key)

            if c > 1:
                this_node = this_node._parent.get(key)

        end_time = time.time()

        self.assertExecutionTime(start_time, end_time, 0.005, 0.6)
        print(".One entry to thirty nested lists", end_time-start_time)

    def test_add_one_hundred_entries_to_thirty_nested_lists(self):
        """
        This test is against sysrepo datastore, when we proxy read/requests from the proxy data store.
        """
        start_time = time.time()
        for d in range(100):
            this_node = self.root.scaling
            for c in range(30):
                if c == 2:
                    key = ('created%sx%s' % (c, d), 'extrakey')
                else:
                    key = ('created%sx%s' % (c, d))
                this_node = this_node['scale%s' % (c)].create(key)
                if c > 1:
                    this_node = this_node._parent.get(key)

        end_time = time.time()

        self.assertExecutionTime(start_time, end_time, 0.45, 0.6)
        print("One hundred entries to thirty nested lists", end_time-start_time)
#
#     def test_write_xml(self):
#         """
#         This test is against sysrepo datastore, when we proxy read/requests from the proxy data store.
#         """
# #        self.root.morecomplex.leaf2 = True
#         self.root.morecomplex.leaf4 = "A"
#         self.root.morecomplex.inner.leaf5 = "this was mandatory"
#         self.root.morecomplex.inner.siblings.a = "a"
#         self.root.morecomplex.inner.siblings.b = "b"
#         x = self.root.container_and_lists.multi_key_list.create("a", "b")
#         x.inner.C = "c"
#         x = self.root.container_and_lists.multi_key_list.create("A", "B")
#         x.inner.C = "C"
#
#         start_time = time.time()
#         for d in range(1):
#             this_node = self.root.scaling
#             for c in range(4):
#                 if c == 2:
#                     key = ('created%sx%s' % (c, d), 'extrakey')
#                 else:
#                     key = ('created%sx%s' % (c, d))
#                 this_node = this_node['scale%s' % (c)].create(key)
#                 if c > 1:
#                     this_node = this_node._parent.get(key)
#                 if c == 3:
#                     for e in range(2):
#                         for f in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
#                             this_node['alpha%s' % (e)].__setattr__(f, 'sdf')
#
#         # Dump to XPATH
#         xpaths = self.session.dump_xpaths()
#
#         start_time = time.time()
#         xmlstr = self.template_ninja.to_xmlstr(xpaths)
#         end_time = time.time()
#         o = open('/tmp/monster.xml', 'w')
#         o.write(xmlstr)
#         o.close()

    def test_add_one_hundred_entries_to_thirty_nested_lists_with_alpha(self):
        """
        This test is against sysrepo datastore, when we proxy read/requests from the proxy data store.
        """

        start_time = time.time()
        for d in range(100):
            this_node = self.root.scaling
            for c in range(30):
                if c == 2:
                    key = ('created%sx%s' % (c, d), 'extrakey')
                else:
                    key = ('created%sx%s' % (c, d))
                this_node = this_node['scale%s' % (c)].create(key)
                if c > 1:
                    this_node = this_node._parent.get(key)
                if c == 29:
                    for e in range(5):
                        for f in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']:
                            this_node['alpha%s' % (e)].__setattr__(f, 'sdf')

        end_time = time.time()
        self.assertExecutionTime(start_time, end_time, 1.3, 0.6)
        print("Add nested leaves with deep data set (16100 items)", end_time-start_time)

        # Template Stuff
        start_time = time.time()
        xpaths = self.session.dump_xpaths()
        end_time = time.time()
        self.assertExecutionTime(start_time, end_time, 0.009, 0.6)
        print(".Dump xpaths with 16100 items)", end_time-start_time)

        # Dump to XPATH
        start_time = time.time()
        xmlstr = self.template_ninja.to_xmlstr(xpaths)
        end_time = time.time()
        self.assertExecutionTime(start_time, end_time, 1.8, 0.6)
        print(".Dump XPATHS to template (16100)", end_time-start_time)

        self.stub.items = {}
        # Dump to XPATH
        start_time = time.time()
        self.template_ninja.from_xmlstr(self.root, xmlstr)
        end_time = time.time()
        self.assertExecutionTime(start_time, end_time, 0.8, 0.6)
        print(".Load XPATHS from xml (16100)", end_time-start_time)

    def test_add_three_thousand_entries_to_one_list(self):
        """
        This test is against sysrepo datastore, when we proxy read/requests from the proxy data store.
        """
        start_time = time.time()
        for d in range(3000):
            this_node = self.root.scaling
            for c in range(1):
                key = ('created%sx%s' % (c, d))
                this_node = this_node['scale%s' % (c)].create(key)
                if c > 1:
                    this_node = this_node._parent.get(key)

        end_time = time.time()
        self.assertExecutionTime(start_time, end_time, 0.27, 0.6)
        print("Add three thousand entries to one list", end_time-start_time)

    def test_change_leaf_3000_times(self):
        """
        This test is against sysrepo datastore, when we proxy read/requests from the proxy data store.
        """
        start_time = time.time()
        for d in range(3000):
            self.root.simpleleaf = "X" + str(d)
            _ = self.root.simpleleaf

        end_time = time.time()
        self.assertExecutionTime(start_time, end_time, 0.08, 0.6)
        print("Simple leaf changed 3000 times", end_time-start_time)
