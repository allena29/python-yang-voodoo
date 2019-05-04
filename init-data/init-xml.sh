#!/bin/bash

cd /working/init-data

if [ "$1" = "" ]
then
	datastore="startup"
else
	datastore="running"
fi

set -euo pipefail

echo "Import $datastore configuration"
for xml in *.xml
do
  module=`echo "$xml" | sed -e 's/\.xml//' | sed -e 's/__.*//'`
  module_with_suffix=`echo "$xml" | sed -e 's/\.xml//'`
  echo "... $module (from file $xml)"
	if [ "$module" = "$module_with_suffix" ]
	then
		sysrepocfg --import=$xml --format=xml --datastore=$datastore $module
	else
		sysrepocfg --merge=$xml --format=xml --datastore=$datastore $module
	fi
done
