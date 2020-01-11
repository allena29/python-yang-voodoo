#!/usr/bin/env python3
import sys
from yangvoodoo.Bridge import startup_client

if __name__ == '__main__':
    uuid = sys.argv[1]
    startup_client(uuid, 'integrationtest', 'yang', '127.0.0.1', '127.0.0.1')
