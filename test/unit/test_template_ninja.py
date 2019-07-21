import yangvoodoo.stubdal
import unittest
from mock import Mock, call, patch


class test_xml_to_xpath(unittest.TestCase):

    maxDiff = 23948230

    def setUp(self):
        self.maxDiff = None
        self.stub = yangvoodoo.stubdal.StubDataAbstractionLayer()
        self.session = yangvoodoo.DataAccess(data_abstraction_layer=self.stub)
        self.session.connect("integrationtest")
        self.root = self.session.get_node()
        self.subject = yangvoodoo.TemplateNinja.TemplateNinja()

        self.schemactx = self.root._context.schemactx
        self.module = self.root._context.module

    def test_xpath_to_xml(self):
        # Build
        xpaths = {
            "/module:regex/abc/def[ghi='s''sdf'][xyz='asd']/ghi": "s''sdf",
            "/module:regex/abc/def[ghi='s''sdf'][xyz='asd']/xyz": "asd",
            "/module:regex/abc/def[ghi='s''sdf'][xyz='asd']/jklm/mnop": "val",
            # "/module:regex/abc/def[ghi='s''sdf'][xyz='asd']/jklm/mnop2": "val2"

        }

        expected_result = """<module>
  <regex>
    <abc>
      <def>
        <ghi>s''sdf</ghi>
        <xyz>asd</xyz>
        <jklm>
          <mnop>val</mnop>
        </jklm>
      </def>
    </abc>
  </regex>
</module>
"""

        # Act
        result = self.subject.to_xmlstr(xpaths)

        # Assert
        self.assertEqual(result, expected_result)

    def test_xpath_to_xml3(self):

        # Build
        xpaths = {
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd']/ghi": "ssdf",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd']/xyz": "asd",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd']/jklm/mnop": "val",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd']/jklm/mnop": "val",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd']/jklm/mnop2": "val2",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd2']/ghi": "ssdf",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd2']/xyz": "asd2",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd2']/jklm/mnop": "val",
            "/module:regex/abc/def[ghi='ssdf'][xyz='asd2']/jklm/mnop2": "val2",
            "/module:regex/abc/zzz": "123"
        }

        expected_result = """<module>
  <regex>
    <abc>
      <def>
        <ghi>ssdf</ghi>
        <xyz>asd</xyz>
        <jklm>
          <mnop>val</mnop>
          <mnop2>val2</mnop2>
        </jklm>
      </def>
      <def>
        <ghi>ssdf</ghi>
        <xyz>asd2</xyz>
        <jklm>
          <mnop>val</mnop>
          <mnop2>val2</mnop2>
        </jklm>
      </def>
      <zzz>123</zzz>
    </abc>
  </regex>
</module>
"""

        # Act
        result = self.subject.to_xmlstr(xpaths)

        # Assert
        self.assertEqual(result, expected_result)

    def test_xpath_to_xml4(self):
        """
        An example template containing lots of embedded lists and
        leaf-lists. The structure of the XML document must change due to that.
        """
        # Build
        path1 = "/integrationtest:container-and-lists/multi-key-list"
        path2 = "/integrationtest:scaling/scale0[key0-a='created0']"
        path3 = path2 + "/scale1[key1-a='created1']/scale2[key2-a='created2'][key2-b='extrakey']"

        xpaths = {
            path1 + "[A='primary-leaf'][B='secondary-leaf']/A": "primary-leaf",
            path1 + "[A='primary-leaf'][B='secondary-leaf']/B": "secondary-leaf",
            path1 + "[A='primary-leaf'][B='secondary-leaf']/inner/C": "c",
            path1 + "[A='primary-leaf'][B='secondary-leaf']/inner/level3list[level3key='key3']/level3key": "key3",
            path1 + "[A='primary-leaf'][B='secondary-leaf']/inner/level3list[level3key='key3']/level3-nonkey": "sdf",
            path1 + "[A='another-leaf'][B='another-leaf']/A": "another-leaf",
            path1 + "[A='another-leaf'][B='another-leaf']/B": "another-leaf",
            "/integrationtest:morecomplex/leaflists/simple": ['abc', '123', 'def'],
            path2 + "/key0-a": "created0",
            path2 + "/scale1[key1-a='created1']/key1-a": "created1",
            path2 + "/scale1[key1-a='created1']/scale2[key2-a='created2'][key2-b='extrakey']/key2-a": "created2",
            path3 + "/key2-b": "extrakey",
            path3 + "/scale3[key3-a='created3']/key3-a": "created3",
            path3 + "/scale3[key3-a='created3']/scale4[key4-a='created4']/key4-a": "created4"
        }

        expected_result = """<integrationtest>
  <container-and-lists>
    <multi-key-list>
      <A>primary-leaf</A>
      <B>secondary-leaf</B>
      <inner>
        <C>c</C>
        <level3list>
          <level3key>key3</level3key>
          <level3-nonkey>sdf</level3-nonkey>
        </level3list>
      </inner>
    </multi-key-list>
    <multi-key-list>
      <A>another-leaf</A>
      <B>another-leaf</B>
    </multi-key-list>
  </container-and-lists>
  <morecomplex>
    <leaflists>
      <simple>abc</simple>
      <simple>123</simple>
      <simple>def</simple>
    </leaflists>
  </morecomplex>
  <scaling>
    <scale0>
      <key0-a>created0</key0-a>
      <scale1>
        <key1-a>created1</key1-a>
        <scale2>
          <key2-a>created2</key2-a>
          <key2-b>extrakey</key2-b>
          <scale3>
            <key3-a>created3</key3-a>
            <scale4>
              <key4-a>created4</key4-a>
            </scale4>
          </scale3>
        </scale2>
      </scale1>
    </scale0>
  </scaling>
</integrationtest>
"""

        # Act
        result = self.subject.to_xmlstr(xpaths)

        # Assert
        self.assertEqual(result, expected_result)

    def test_template_ninja_with_xpath_looking_keys(self):
        path = "/integrationtest:container-and-lists/multi-key-list[A='/this/looks/a/bit/like/xpath[key=\"sdf\"]/sdf']"
        xpaths = {
            path + "[B='second-leaf']/A": "/this/looks/a/bit/like/xpath[key=\"sdf\"]/sdf",
            path + "[B='second-leaf']/B": "second-leaf",
            path + "[B='second-leaf']/inner/C": "C",
        }

        # Act
        result = self.subject.to_xmlstr(xpaths)

        # Assert
        expected_result = """<integrationtest>
  <container-and-lists>
    <multi-key-list>
      <A>/this/looks/a/bit/like/xpath[key="sdf"]/sdf</A>
      <B>second-leaf</B>
      <inner>
        <C>C</C>
      </inner>
    </multi-key-list>
  </container-and-lists>
</integrationtest>
"""
        self.assertEqual(result, expected_result)

    def test_from_template_siblings(self):
        # Build

        template = """<integrationtest>
          <morecomplex>
            <inner>
              <siblings>
                <a>A</a>
                <b>B</b>
                <c>C</c>
                <d>D</d>
                <e>E</e>
                <f>F</f>
                <g>G</g>
                <h>H</h>
              </siblings>
            </inner>
          </morecomplex>
        </integrationtest>
        """

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, self.stub)

        # assert
        self.assertEqual(self.root.morecomplex.inner.siblings.a, "A")
        self.assertEqual(self.root.morecomplex.inner.siblings.b, "B")
        self.assertEqual(self.root.morecomplex.inner.siblings.c, "C")
        self.assertEqual(self.root.morecomplex.inner.siblings.d, "D")
        self.assertEqual(self.root.morecomplex.inner.siblings.e, "E")
        self.assertEqual(self.root.morecomplex.inner.siblings.f, "F")
        self.assertEqual(self.root.morecomplex.inner.siblings.g, "G")
        self.assertEqual(self.root.morecomplex.inner.siblings.h, "H")

    def test_from_template_choices(self):
        # Build

        template = """<integrationtest>
          <morecomplex>
            <inner>
              <beer-styles>
                <beer-style>new-england</beer-style>
                <beer-choice>
                  <new-england-case>
                    <hazy-style>
                      <beer-chosen>hazy jane</beer-chosen>
                      <rating>5</rating>
                      <size>schooner</size>
                    </hazy-style>
                  </new-england-case>
                </beer-choice>
              </beer-styles>
            </inner>
          </morecomplex>
        </integrationtest>
        """

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, self.stub)

        # assert
        self.assertEqual(repr(self.root.morecomplex.inner.beer_styles['new-england']),
                         "VoodooListElement{/integrationtest:morecomplex/inner/beer-styles[beer-style='new-england']}")

        self.assertEqual(self.root.morecomplex.inner.beer_styles['new-england'].beer_choice.new_england_case.hazy_style.beer_chosen, "hazy jane")
        self.assertEqual(self.root.morecomplex.inner.beer_styles['new-england'].beer_choice.new_england_case.hazy_style.rating, 5)
        self.assertEqual(self.root.morecomplex.inner.beer_styles['new-england'].beer_choice.new_england_case.hazy_style.size, "schooner")

    def test_from_template_A(self):
        # Build

        template = """<integrationtest>
          <container-and-lists>
            <numberkey-list>
              <numberkey>5</numberkey>
              <description>FIVE</description>
            </numberkey-list>
            <multi-key-list>
              <A>a</A>
              <B>b</B>
              <inner>
                <level3list>
                  <level3key>33333</level3key>
                  <level3-nonkey>three</level3-nonkey>
                </level3list>
              </inner>
              <level2list>
                <level2key>22222</level2key>
              </level2list>
            </multi-key-list>
          </container-and-lists>
        </integrationtest>
        """

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, self.stub)

        # assert
        self.assertEqual(len(self.root.container_and_lists.multi_key_list['a', 'b'].inner.level3list), 1)
        self.assertEqual(self.root.container_and_lists.multi_key_list['a', 'b'].inner.level3list['33333'].level3key, '33333')
        self.assertEqual(self.root.container_and_lists.multi_key_list['a', 'b'].level2list['22222'].level2key, '22222')
        self.assertFalse('2' in self.root.container_and_lists.multi_key_list.level2list)

    def test_from_template_with_the_wrong_keys(self):
        # Build

        template = """<integrationtest>
          <container-and-lists>
            <numberkey-list>
              <numberkey>5</numberkey>
            </numberkey-list>
            <multi-key-list>
              <B>a</B>
              <A>b</A>
            </multi-key-list>
          </container-and-lists>
        </integrationtest>
        """

        dal = Mock()

        # Act
        with self.assertRaises(ValueError) as context:
            self.subject._import_xml_to_datastore(self.module, self.schemactx, template, dal)

        # Assert
        expected_msg = "Expecting key name A, got B at /integrationtest:container-and-lists/multi-key-list"
        self.assertEqual(expected_msg, str(context.exception))

    def test_from_template_with_only_keys(self):
        # Build

        template = """<integrationtest>
          <container-and-lists>
            <numberkey-list>
              <numberkey>5</numberkey>
            </numberkey-list>
            <multi-key-list>
              <A>a</A>
              <B>b</B>
            </multi-key-list>
          </container-and-lists>
        </integrationtest>
        """

        dal = Mock()

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, dal)

        # Assert
        self.assertEqual(dal.create.call_count, 2)
        dal.create.assert_has_calls([
            call("/integrationtest:container-and-lists/numberkey-list[numberkey='5']", ['numberkey'],
                 [(5, 19)], list_xpath='/integrationtest:container-and-lists/numberkey-list'),
            call("/integrationtest:container-and-lists/multi-key-list[A='a'][B='b']", ['A', 'B'],
                 [('a', 18), ('b', 18)], list_xpath='/integrationtest:container-and-lists/multi-key-list')
        ])

    def test_from_template_with_union_of_enumeartions(self):
        # Build

        template = """<integrationtest>
          <morecomplex>
            <inner>
                <leaf112>vocation</leaf112>
            </inner>
        </morecomplex>
        </integrationtest>
        """

        dal = Mock()

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, dal)

        # Assert
        self.assertEqual(dal.set.call_count, 1)
        dal.set.assert_has_calls([
            call('/integrationtest:morecomplex/inner/leaf112', 'vocation', 11),
        ])

    def test_from_template_with_union_of_enumeartions_but_setting_integer(self):
        # Build

        template = """<integrationtest>
          <morecomplex>
            <inner>
                <leaf112>123</leaf112>
            </inner>
        </morecomplex>
        </integrationtest>
        """

        dal = Mock()

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, dal)

        # Assert
        self.assertEqual(dal.set.call_count, 1)
        dal.set.assert_has_calls([
            call('/integrationtest:morecomplex/inner/leaf112', 123, 21),
        ])
    #
    # def test_from_template_with_union_of_enumeartions_but_setting_boolean(self):
    # TODO: Union of enumeration + boolean not support yet
    #     # Build
    #
    #     template = """<integrationtest>
    #       <morecomplex>
    #         <inner>
    #             <leaf113>true</leaf113>
    #         </inner>
    #     </morecomplex>
    #     </integrationtest>
    #     """
    #
    #     dal = Mock()
    #
    #     # Act
    #     self.subject._import_xml_to_datastore(self.module, self.schemactx, template, dal)
    #
    #     # Assert
    #     self.assertEqual(dal.set.call_count, 1)
    #     dal.set.assert_has_calls([
    #         call('/integrationtest:morecomplex/inner/leaf112', 123, 21),
    #     ])

    def test_from_template_with_leaflists(self):
        # Build

        template = """<integrationtest>
          <morecomplex>
            <leaflists>
                <simple>A</simple>
                <simple>Z</simple>
                <simple>M</simple>
            </leaflists>
        </morecomplex>
        </integrationtest>
        """

        dal = Mock()

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, dal)

        # Assert
        self.assertEqual(dal.create.call_count, 0)
        self.assertEqual(dal.add.call_count, 3)
        dal.add.assert_has_calls([
            call("/integrationtest:morecomplex/leaflists/simple", 'A', 18),
            call("/integrationtest:morecomplex/leaflists/simple", 'Z', 18),
            call("/integrationtest:morecomplex/leaflists/simple", 'M', 18)
        ])

    def test_from_template_with_leaflists_with_stub_dal(self):
        # Build

        template = """<integrationtest>
          <morecomplex>
            <leaflists>
                <simple>A</simple>
                <simple>Z</simple>
                <simple>M</simple>
            </leaflists>
        </morecomplex>
        </integrationtest>
        """

        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, self.stub)

        # Assert
        expected_items = ['A', 'Z', 'M']
        self.assertEqual(len(self.root.morecomplex.leaflists.simple), 3)
        for item in self.root.morecomplex.leaflists.simple:

            self.assertEqual(expected_items[0], item)
            expected_items.pop(0)

    @patch("builtins.open", create=True)
    def test_from_template(self, mockOpen):
        # Build
        moca = Mock()
        moca.render.return_value = "Rendered Template"
        self.subject._getTemplate = Mock(return_value=moca)
        mockOpen.read.return_value = 'template-contents'
        self.subject._import_xml_to_datastore = Mock()

        # Act
        self.subject.from_template(self.root, "my_template_file.xml", keyword1=1, keyword2=2)

        # Assert
        self.subject._import_xml_to_datastore.assert_called_once_with('integrationtest', self.root._context.schemactx,
                                                                      "Rendered Template", self.root._context.dal)

        moca.render.assert_called_once_with({'root': self.root, 'keyword1': 1, 'keyword2': 2})

    def test_from_xmlstr(self):
        # Build
        self.subject._import_xml_to_datastore = Mock()

        # Act
        self.subject.from_xmlstr(self.root, "<my-xmlstr/>")

        # Assert
        self.subject._import_xml_to_datastore.assert_called_once_with('integrationtest', self.root._context.schemactx,
                                                                      '<my-xmlstr/>', self.root._context.dal)

    def test_from_template_with_list_number(self):
        # Build

        template = """<integrationtest>
          <container-and-lists>
            <numberkey-list>
              <numberkey>5</numberkey>
            </numberkey-list>
            <numberkey-list>
              <numberkey>6</numberkey>
              <description>SIX</description>
            </numberkey-list>
            <numberkey-list>
              <numberkey>7</numberkey>
              <description>SEVEN</description>
            </numberkey-list>
          </container-and-lists>
        </integrationtest>
        """
        # Act
        self.subject._import_xml_to_datastore(self.module, self.schemactx, template, self.stub)

        self.assertEqual(len(self.root.container_and_lists.numberkey_list), 3)

        self.assertEqual(self.root.container_and_lists.numberkey_list[5].numberkey, 5)
        self.assertEqual(self.root.container_and_lists.numberkey_list[6].numberkey, 6)
        self.assertEqual(self.root.container_and_lists.numberkey_list[7].numberkey, 7)
        self.assertEqual(['description', 'numberkey'], list(dir(self.root.container_and_lists.numberkey_list[6])))
        self.assertEqual(("/integrationtest:container-and-lists/numberkey-list"
                          "[numberkey='6']"),
                         self.root.container_and_lists.numberkey_list[6]._path)

        self.assertEqual(self.root.container_and_lists.numberkey_list[6].description, 'SIX')
        self.assertEqual(self.root.container_and_lists.numberkey_list[7].description, 'SEVEN')

    def test_from_template_with_jinja2_processing(self):
        # Build
        self.root.simpleleaf = 'GOODBYE'

        # Act
        self.root.from_template('test/unit/test.xml')

        # Assert
        self.assertEqual(self.root.simpleleaf, 'HELLO')
        self.assertEqual(self.root.default, 'GOODBYE')


class dummy_iterator:

    def __init__(self, list_items):
        self.list_items = list_items
        self.i = 0

    def keys(self):
        return self

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= len(self.list_items):
            raise StopIteration()
        self.i = self.i + 1
        return self.list_items[self.i-1]
