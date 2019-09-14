import pytest
from yangvoodoo.pyro4dal import PyroDataAbstractionLayer


@pytest.fixture
def subject():
    session = PyroDataAbstractionLayer()
    print(session)
    session.pyro4_connect('192.168.3.1', '192.168.1.28')

    yield session


def test_simplest_get_possible(subject):
    leaf_val = subject.get('/integrationtest:simpleleaf', 'default')

    assert leaf_val == 'default'
