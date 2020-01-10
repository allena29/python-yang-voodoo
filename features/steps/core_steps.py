import os
import signal
import subprocess
import time

import Pyro4
from behave import when, given, then


@given("we stop any '{yangmodel}' datastore-bridges")
def step_impl_stop_datastore_bridges(behave_context, yangmodel):
    pid_file = 'pid/' + yangmodel + '.pid'
    if os.path.exists(pid_file):
        with open(pid_file) as pid_handle:
            pid_string = pid_handle.read().rstrip()
        pid = int(pid_string)
        try:
            os.kill(pid, signal.SIGTERM)
        except Exception:
            os.remove(pid_file)

        while True:
            if not os.path.exists(pid_file):
                break
            time.sleep(0.5)


@when("we delete any existing data for '{yangmodel}'")
@given("we delete any existing data for '{yangmodel}'")
def step_impl_delete_existing_data(behave_context, yangmodel):
    """
    Note: this should be done without a datastore-bridge running.
    """
    datastore_file = 'datstore/' + yangmodel+'.persist'
    if os.path.exists(datastore_file):
        os.remove(datastore_file)


@given("we start a datastore-bridge for '{yangmodel}'")
def step_impl_start_bridge_for_yang_model(behave_context, yangmodel):
    behave_context.datastore_bridge = subprocess.Popen(['python3', 'datastore-gatekeeper.py'])
    pid_file = 'pid/' + yangmodel+'.pid'
    if os.path.exists(pid_file):
        raise ValueError('pid file exist already')
    time.sleep(0.5)
    while True:
        if os.path.exists(pid_file):
            break
        time.sleep(0.2)
    time.sleep(0.5)


@then('the following file should exist {filename}')
def step_impl_file_should_exist(behave_context, filename):
    if not os.path.exists(filename):
        assert False, "File %s should exist but does not" % (filename)


@then('the following file should not exist {filename}')
def step_impl_should_not_exist(behave_context, filename):
    if os.path.exists(filename):
        assert False, "File %s should not exist but does" % (filename)


@when("we start a new candidate transaction for '{yangmodel}'")
def step_implnew_candidate_transaction(behave_context, yangmodel):
    uri = behave_context.ns.lookup("net.mellon-collie.yangvooodoo.VoodooGatekeeper." + behave_context.hostname + '.' + yangmodel)
    behave_context.obj = Pyro4.Proxy(uri)
    behave_context.obj._pyroHmacKey = behave_context.hmac_key
    behave_context.uuid = behave_context.obj.start_transaction()


@then("we should be given a transaction-id.")
def step_impl_we_should_have_a_transaction_id(behave_context):
    if behave_context.uuid is None:
        assert False, "No transaction id"
