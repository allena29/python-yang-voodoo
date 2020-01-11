
from yangvoodoo import Merge

#
# def test_merge_schema_and_data_trees_with_no_data():
#     # Arrange
#     subject = Merge.DataSchema('form', 'form-section',   yang_location='yang/')
#
#     # Assert
#     result = list(subject.process())
#
#     # Assert
#     expected_result = [
#         ('/form:topleaf', '/form:topleaf', None),
#         ('/form:middleleaf', '/form:middleleaf', None),
#         ('/form:bottomleaf', '/form:bottomleaf', None),
#     ]
#
#     assert result == expected_result
#

#
# def test_merge_schema_and_data_trees():
#     # Arrange
#     subject = Merge.DataSchema('form', 'form-section',  'json', ['test/resources/form.json'], 'yang/')
#
#     # Assert
#     result = list(subject.process())
#
#     print(result)
#     # Assert
#     expected_result = [
#         ('/form:topleaf', '/form:topleaf', 'AAAAA'),
#         ('/form:toplevel-list/one', '/form:toplevel-list/form:one', None),
#         ('/form:toplevel-list/three', '/form:toplevel-list/form:two/form:three', None),
#         ('/form:toplevel-list/four', '/form:toplevel-list/form:four', None),
#         ('/form:form-section/hello', '/form:form-section/form:hello', None),
#         ('/form:form-section/a', '/form:form-section/form:abc/form:a', None),
#         ('/form:form-section/c', '/form:form-section/form:abc/form:b/form:c', None),
#         ('/form:form-section/x', '/form:form-section/form:abc/form:b/form:xyz/form:x', None),
#         ('/form:form-section/z', '/form:form-section/form:abc/form:b/form:xyz/form:y/form:z', None),
#         ('/form:middleleaf', '/form:middleleaf', None),
#         ('/form:footer-form/goodbye', '/form:footer-form/form:goodbye', None),
#         ('/form:bottomleaf', '/form:bottomleaf', None),
#
#     ]
#
#     for r in result:
#         print(r)
#     assert expected_result == result


def test_merge_schema_and_data_trees_top_level_list():
    # Arrange
    subject = Merge.DataSchema('form', 'form-section',  'xml', ['test/resources/form.xml'], 'yang/')

    # Assert
    result = list(subject.process())

    print(result)
    # Assert
    expected_result = [
        ('/form:topleaf', '/form:topleaf', None),
        ('/form:toplevel-list/one', '/form:toplevel-list/form:one', 'a'),
        ('/form:toplevel-list/three', '/form:toplevel-list/form:two/form:three', None),
        ('/form:toplevel-list/four', '/form:toplevel-list/form:four', '4'),
        ('/form:form-section/hello', '/form:form-section/form:hello', None),
        ('/form:form-section/a', '/form:form-section/form:abc/form:a', None),
        ('/form:form-section/c', '/form:form-section/form:abc/form:b/form:c', None),
        ('/form:form-section/x', '/form:form-section/form:abc/form:b/form:xyz/form:x', None),
        ('/form:form-section/z', '/form:form-section/form:abc/form:b/form:xyz/form:y/form:z', None),
        ('/form:middleleaf', '/form:middleleaf', None),
        ('/form:footer-form/goodbye', '/form:footer-form/form:goodbye', None),
        ('/form:bottomleaf', '/form:bottomleaf', None),

    ]

    for r in result:
        print(r)
    assert expected_result == result
