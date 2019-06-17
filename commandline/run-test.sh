#!/bin/bash

overall=0

echo ""
echo "LINT Checks.. Command Line"
pycodestyle ./
if [ $? != 0 ]
then
  exit 1;
fi


echo ""
echo "Unit tests.. Command Line"
python3 -m unittest discover test
if [ $? != 0 ]
then
  exit 1;
fi
