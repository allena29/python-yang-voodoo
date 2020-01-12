from mock import ANY
from yangvoodoo import Merge


def test_getting_all_data_paths_based_on_a_schmea_tree():
    # Arrange
    subject = Merge.DataSchema('form', 'form-section',  'xml', ['test/resources/form.xml'], 'yang/')

    # Assert
    result = list(subject._get_all_data_paths())

    # Assert
    expected_result = [
        ("/form:topleaf", None, ANY),
        ("/form:toplevel-list", "[one='%s']", ANY),
        ("/form:toplevel-list[one='%s']/one", None, ANY),
        ("/form:toplevel-list[one='%s']/two", None, ANY),
        ("/form:toplevel-list[one='%s']/two/three", None, ANY),
        ("/form:toplevel-list[one='%s']/four", None, ANY),
        ("/form:composite-list", "[one='%s'][five='%s']", ANY),
        ("/form:composite-list[one='%s'][five='%s']/one", None, ANY),
        ("/form:composite-list[one='%s'][five='%s']/five", None, ANY),
        ("/form:composite-list[one='%s'][five='%s']/two", None, ANY),
        ("/form:composite-list[one='%s'][five='%s']/two/three", None, ANY),
        ("/form:composite-list[one='%s'][five='%s']/four", None, ANY),
        ("/form:form-section", None, ANY),
        ("/form:form-section/hello", None, ANY),
        ("/form:form-section/abc", "[a='%s']", ANY),
        ("/form:form-section/abc[a='%s']/a", None, ANY),
        ("/form:form-section/abc[a='%s']/b", None, ANY),
        ("/form:form-section/abc[a='%s']/b/c", None, ANY),
        ("/form:form-section/abc[a='%s']/b/xyz", "[x='%s']", ANY),
        ("/form:form-section/abc[a='%s']/b/xyz[x='%s']/x", None, ANY),
        ("/form:form-section/abc[a='%s']/b/xyz[x='%s']/y", None, ANY),
        ("/form:form-section/abc[a='%s']/b/xyz[x='%s']/y/z", None, ANY),
        ("/form:middleleaf", None, ANY),
        ("/form:footer-form", None, ANY),
        ("/form:footer-form/goodbye", None, ANY),
        ("/form:bottomleaf", None, ANY)
    ]

    assert result == expected_result


def test_predicate_map():
    # Arrange
    subject = Merge.DataSchema('form', 'form-section',  'xml', ['test/resources/form.xml'], 'yang/')

    # Act
    subject._build_map_of_predicates()
    result = subject.predicate_map

    # Assert
    expected_result = {
        "/form:toplevel-list[one='%s']": ["/form:toplevel-list[one='a']", "/form:toplevel-list[one='b']"],
        "/form:composite-list[one='%s'][five='%s']": [],
        "/form:form-section/abc[a='%s']": [],
        "/form:form-section/abc[a='%s']/b/xyz[x='%s']": []
    }

    assert expected_result == result


def test_predicate_path_count():
    # Arrange
    subject = Merge.DataSchema('form', 'form-section',  'xml', ['test/resources/form.xml'], 'yang/')

    # Act
    subject._build_map_of_predicates()
    result = subject.predicate_path_count

    # Assert
    expected_result = {
        "/form:toplevel-list[one='%s']": 4,
        "/form:composite-list[one='%s'][five='%s']": 5,
        "/form:form-section/abc[a='%s']": 3,
        "/form:form-section/abc[a='%s']/b/xyz[x='%s']": 3
    }

    assert expected_result == result
