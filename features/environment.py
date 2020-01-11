import os
import signal

import time

import Pyro4


def before_scenario(behave_context, scenario):
    behave_context.ns = Pyro4.locateNS()
    behave_context.hostname = '127.0.0.1'
    behave_context.hmac_key = 'this-value-is-a-dummy-hmac-key'
    behave_context.uuid = None


def after_scenario(behave_context, scenario):
    print('waiting 30 seconds for debug')
    try:
        time.sleep(30)
    except KeyboardInterrupt:
        pass
    if behave_context.uuid:
        candidate_session = f'candidate/{behave_context.uuid}.session'
        print(f'Terminating candidate session for {candidate_session}')
        with open(f'{candidate_session}') as fh:
            pid = int(fh.read())
            os.kill(pid, signal.SIGTERM)
            os.unlink(candidate_session)
