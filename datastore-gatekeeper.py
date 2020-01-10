#!/usr/bin/env python3

import signal

from yangvoodoo.Bridge import startup_gatekeeper, cleanexit

if __name__ == '__main__':
    signal.signal(signal.SIGINT, cleanexit)
    signal.signal(signal.SIGTERM, cleanexit)
    startup_gatekeeper('integrationtest', 'yang', '127.0.0.1', '127.0.0.1')
