#!/bin/bash

sysrepod
redis-server &
#sysrepo-plugind
# netopeer2-server

echo "Importing YANG"
cd /working/yang
./install-yang.sh

sleep 15

echo "Importing Initial Data"
cd /working/init-data
./init-xml.sh

echo "Starting subscribers"
cd /working/subscribers
./launch-subscribers.sh

touch /tmp/sysrepod-just-launched
sleep 5
echo "Ready"
set -euo pipefail

./run-test.sh
