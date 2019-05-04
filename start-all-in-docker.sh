#!/bin/bash

set -euxo pipefail

sysrepod
sysrepo-plugind
netopeer2-server
cd /working/yang
./install-yang.sh
cd /working/init-data
./init-xml.sh
cd /working/subscribers
./launch-subscribers.sh

echo "Ready"
cd /working/web-frontend
python3 app.py 
/bin/bash
