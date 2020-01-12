from mock import ANY
from yangvoodoo import Merge


def test_getting_all_data_paths_based_on_a_schmea_tree():
    # Arrange
    subject = Merge.DataSchema('form', 'xml', ['test/resources/form.xml'], 'yang/')

    # Assert
    result = list(subject._get_all_data_paths())

    # Assert
    expected_result = [
        ("/form:topleaf", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:toplevel-list", "[one='%s']", ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:toplevel-list[one='%s']/one", None, ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='%s']/two", None, ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='%s']/two/three", None, ANY, 'b15871681f832be39030a7b142f2b54b8484f525'),
        ("/form:toplevel-list[one='%s']/four", None, ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:composite-list", "[one='%s'][five='%s']", ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:composite-list[one='%s'][five='%s']/one", None, ANY,  '6b87dab11d546afe2faa86a6d2cb31e38d266977'),
        ("/form:composite-list[one='%s'][five='%s']/five", None, ANY, '6b87dab11d546afe2faa86a6d2cb31e38d266977'),
        ("/form:composite-list[one='%s'][five='%s']/two", None, ANY,  '6b87dab11d546afe2faa86a6d2cb31e38d266977'),
        ("/form:composite-list[one='%s'][five='%s']/two/three", None, ANY, '933b7ea5da997fb759732943f35dca59e5925c30'),
        ("/form:composite-list[one='%s'][five='%s']/four", None, ANY, '6b87dab11d546afe2faa86a6d2cb31e38d266977'),
        ("/form:form-section", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:form-section/hello", None, ANY,  'dbefc2a2fa24e6415280852de37e40df16b9a49a'),
        ("/form:form-section/abc", "[a='%s']",  ANY, 'dbefc2a2fa24e6415280852de37e40df16b9a49a'),
        ("/form:form-section/abc[a='%s']/a", None, ANY,  'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1'),
        ("/form:form-section/abc[a='%s']/b", None, ANY, 'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1'),
        ("/form:form-section/abc[a='%s']/b/c", None, ANY, '1c286d6bb9056c56f57445e6418adff0e238c75e'),
        ("/form:form-section/abc[a='%s']/b/xyz", "[x='%s']",  ANY,  '1c286d6bb9056c56f57445e6418adff0e238c75e'),
        ("/form:form-section/abc[a='%s']/b/xyz[x='%s']/x", None, ANY, '7d906e4cc4deae3a81743ddd13da623566f59db5'),
        ("/form:form-section/abc[a='%s']/b/xyz[x='%s']/y", None, ANY, '7d906e4cc4deae3a81743ddd13da623566f59db5'),
        ("/form:form-section/abc[a='%s']/b/xyz[x='%s']/y/z", None, ANY,  'ad1361eea6dc1b40c6bea4b36d783cf3223d04eb'),
        ("/form:middleleaf", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:footer-form", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:footer-form/goodbye", None, ANY, '54a927f48a4409c13e72d483f72a31c38de149ce'),
        ("/form:bottomleaf", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
    ]

    assert result == expected_result


def test_structure_map():
    # Arrange
    subject = Merge.DataSchema('form',  'xml', ['test/resources/form.xml'], 'yang/')

    # Act
    list(subject.process())
    result = subject.structures

    # Assert
    expected_result = {
        'da39a3ee5e6b4b0d3255bfef95601890afd80709': '',
        '38f697830d29188847b6d756cb7239e20e22f043': '/form:toplevel-list',
        'b15871681f832be39030a7b142f2b54b8484f525': '/form:toplevel-list/form:two',
        '6b87dab11d546afe2faa86a6d2cb31e38d266977': '/form:composite-list',
        '933b7ea5da997fb759732943f35dca59e5925c30': '/form:composite-list/form:two',
        'dbefc2a2fa24e6415280852de37e40df16b9a49a': '/form:form-section',
        'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1': '/form:form-section/form:abc',
        '1c286d6bb9056c56f57445e6418adff0e238c75e': '/form:form-section/form:abc/form:b',
        '7d906e4cc4deae3a81743ddd13da623566f59db5': '/form:form-section/form:abc/form:b/form:xyz',
        'ad1361eea6dc1b40c6bea4b36d783cf3223d04eb': '/form:form-section/form:abc/form:b/form:xyz/form:y',
        '54a927f48a4409c13e72d483f72a31c38de149ce': '/form:footer-form'
    }

    assert expected_result == result


def test_predicate_map():
    # Arrange
    subject = Merge.DataSchema('form',  'xml', ['test/resources/form.xml'], 'yang/')

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
    subject = Merge.DataSchema('form',  'xml', ['test/resources/form.xml'], 'yang/')

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


def test_process():
    # Arrange
    subject = Merge.DataSchema('form',  'xml', ['test/resources/form.xml'], 'yang/')

    # Act
    result = list(subject.process())

    # Assert
    expected_result = [
        ('/form:topleaf', None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:toplevel-list[one='a']", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:toplevel-list[one='a']/one", 'a', ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='a']/two", True, ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='a']/two/three", '3', ANY, 'b15871681f832be39030a7b142f2b54b8484f525'),
        ("/form:toplevel-list[one='a']/four", '4', ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='b']", None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ("/form:toplevel-list[one='b']/one", 'b', ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='b']/two", True, ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ("/form:toplevel-list[one='b']/two/three", 'b3', ANY, 'b15871681f832be39030a7b142f2b54b8484f525'),
        ("/form:toplevel-list[one='b']/four", 'b4', ANY, '38f697830d29188847b6d756cb7239e20e22f043'),
        ('/form:form-section', True, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:form-section/hello', None, ANY, 'dbefc2a2fa24e6415280852de37e40df16b9a49a'),
        ('/form:middleleaf', None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:footer-form', True, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:footer-form/goodbye', None, ANY, '54a927f48a4409c13e72d483f72a31c38de149ce'),
        ('/form:bottomleaf', None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
    ]
    assert expected_result == result


def test_process_from_json():
    # Arrange
    subject = Merge.DataSchema('form', 'json', ['test/resources/form.json'], 'yang/')

    # Act
    result = list(subject.process())

    # Assert
    expected_result = [
        ('/form:topleaf', 'ABCTOPLEAF', ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:form-section', True, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:form-section/hello', None, ANY, 'dbefc2a2fa24e6415280852de37e40df16b9a49a'),
        ("/form:form-section/abc[a='1']", None, ANY, 'dbefc2a2fa24e6415280852de37e40df16b9a49a'),
        ("/form:form-section/abc[a='1']/a", '1', ANY, 'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1'),
        ("/form:form-section/abc[a='1']/b", True, ANY, 'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1'),
        ("/form:form-section/abc[a='1']/b/c", None, ANY, '1c286d6bb9056c56f57445e6418adff0e238c75e'),
        ("/form:form-section/abc[a='2']", None, ANY, 'dbefc2a2fa24e6415280852de37e40df16b9a49a'),
        ("/form:form-section/abc[a='2']/a", '2', ANY, 'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1'),
        ("/form:form-section/abc[a='2']/b", True, ANY, 'd84423181e0f6d9ee9fe260e1ccf2227d2e71cd1'),
        ("/form:form-section/abc[a='2']/b/c", None, ANY, '1c286d6bb9056c56f57445e6418adff0e238c75e'),
        ('/form:middleleaf', None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:footer-form', True, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709'),
        ('/form:footer-form/goodbye', None, ANY, '54a927f48a4409c13e72d483f72a31c38de149ce'),
        ('/form:bottomleaf', None, ANY, 'da39a3ee5e6b4b0d3255bfef95601890afd80709')
    ]
    assert expected_result == result
