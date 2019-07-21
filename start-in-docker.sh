#!/bin/bash

sysrepod
redis-server &
#sysrepo-plugind
# netopeer2-server

echo "Importing YANG"
cd /working/yang
./install-yang.sh

echo "Importing Initial Data"
cd /working/init-data
./init-xml.sh

echo "Starting subscribers"
cd /working/subscribers
./launch-subscribers.sh

touch /tmp/sysrepod-just-launched

echo "Ready"
cd /working
if [ -f "/builder" ]
then
  ./run-test.sh
fi

if [ $? = 0 ]
then
  ./interactive
fi
/bin/bash
