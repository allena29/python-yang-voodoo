import subprocess
import threading
import time

import pytest
from yangvoodoo.pyro4dal import PyroDataAbstractionLayer


def open_datastore_bridge_in_thread(thread_info):
    process = subprocess.Popen(["./datastore-bridge.py"],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    thread_info['process'] = process
    thread_info['pid'] = process.pid
    out, err = process.communicate('')


@pytest.fixture(scope='session', autouse=True)
def dal_bridge():
    thread_info = {}
    dal_bridge_thread = threading.Thread(target=open_datastore_bridge_in_thread, args=(thread_info,))
    dal_bridge_thread.start()
    time.sleep(0.3)

    yield dal_bridge

    thread_info['process'].kill()


@pytest.fixture
def subject():
    session = PyroDataAbstractionLayer()
    session.pyro4_connect('192.168.3.1', '192.168.1.28')
    yield session


def test_simplest_get_possible_default_value_because_leaf_does_not_exist(subject):
    leaf_val = subject.get('/integrationtest:simpleleaf', 'default')
    assert leaf_val == 'default'


def test_simplest_get_possible_default_value_because_laf_does_not_exist(subject):
    leaf_val = subject.set('/integrationtest:simpleleaf', 'defaultx')
    leaf_val = subject.get('/integrationtest:simpleleaf', 'defaulty')
    assert leaf_val == 'defaultx'


def test_has_item_for_nonexisting_item(subject):
    result = subject.has_item("/integrationtest:simplelist[simplekey='x']")
    assert result is False


def test_containers(subject):
    result = subject.container('/integrationtest:morecomplex/inner')
    assert result is False

    result = subject.create_container('/integrationtest:morecomplex/inner')

    result = subject.container('/integrationtest:morecomplex/inner')
    assert result is True


def test_leaflist_things(subject):
    result = subject.gets_len('/integrationtest:morecomplex/leaflists/simple')
    assert result == 0

    subject.add('/integrationtest:morecomplex/leaflists/simple', 'a', 10)

    result = subject.gets_len('/integrationtest:morecomplex/leaflists/simple')
    assert result == 1

    result = list(subject.gets('/integrationtest:morecomplex/leaflists/simple'))
    assert result == ['a']

    subject.add('/integrationtest:morecomplex/leaflists/simple', 'b', 10)
    subject.add('/integrationtest:morecomplex/leaflists/simple', 'c', 10)

    result = subject.gets_len('/integrationtest:morecomplex/leaflists/simple')
    assert result == 3

    result = list(subject.gets('/integrationtest:morecomplex/leaflists/simple'))
    assert result == ['a', 'b', 'c']

    result = subject.remove('/integrationtest:morecomplex/leaflists/simple', 'b')

    result = list(subject.gets('/integrationtest:morecomplex/leaflists/simple'))
    assert result == ['a', 'c']


def test_list_things(subject):
    subject.create("/integrationtest:simplelist[simplekey='y']", keys=['simplekey'],
                   values=[('y', 10)], module='integrationtest')
    result = subject.has_item("/integrationtest:simplelist[simplekey='y']")

    assert result is True

    result = list(subject.gets_unsorted("/integrationtest:simplelist", "/integrationtest:simplelist"))
    assert result == ["/integrationtest:simplelist[simplekey='a']",
                      "/integrationtest:simplelist[simplekey='y']"]

    result = subject.gets_len('/integrationtest:simplelist')

    assert result == 2
    subject.uncreate("/integrationtest:simplelist[simplekey='y']")
    result = subject.has_item("/integrationtest:simplelist[simplekey='y']")
    assert result is False

    result = subject.gets_len('/integrationtest:simplelist')
    assert result == 1


def test_simplest_get_possible(subject):
    leaf_val = subject.get('/integrationtest:morecomplex/leaf4', 'default')
    assert leaf_val == 'A'


def test_simplest_set_then_get(subject):
    subject.set('/integrationtest:morecomplex/leaf3', 4)
    leaf_val = subject.get('/integrationtest:morecomplex/leaf3', 4)
    assert leaf_val == 4


def test_dumps(subject):
    subject.create("/integrationtest:container-and-lists/multi-key-list[A='y'][B='z']",
                   keys=['A', 'B'], values=[('y', 10), ('z', 10)], module='integrationtest')

    # Act
    result = subject.dumps(1)

    # Assert
    expected_xml = """<simplelist xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><simplekey>a</simplekey><nonleafkey>5</nonleafkey></simplelist><morecomplex xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><leaf4>A</leaf4><leaflists><simple>a</simple><simple>c</simple></leaflists><inner/><leaf3>4</leaf3></morecomplex><container-and-lists xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest"><multi-key-list><A>y</A><B>z</B></multi-key-list></container-and-lists><simpleleaf xmlns="http://brewerslabng.mellon-collie.net/yang/integrationtest">defaultx</simpleleaf>"""
    print(result)

    assert result == expected_xml
