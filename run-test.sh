#!/bin/bash

testtype="all"
if [ "$1" = "unit" ]
then
  testtype="unit"
fi

set pipefail -euo

printf "\n\e[1;33mLint checks.....\e[0m\n"
pycodestyle yangvoodoo/
if [ $? != 0 ]
then
  printf "\n\e[1;31Lint checks.. Failed\e[0m\n"
  exit 1;
else
  printf "\n\e[1;32mLint checks.. Passed\e[0m\n"
fi

printf "\n\e[1;33mComplexity checks.....\e[0m\n"
# xenon . -a C -m C -b C
xenon yangvoodoo -a C -m C -b C 2>/dev/stdout| grep -v '_find_best_number_type" has a rank of D' | grep ERROR
if [ $? == 0 ]
then
  printf "\n\e[1;31mComplexity checkss.. Failed\e[0m\n"
  exit 1;
else
  printf "\n\e[1;32mComplexity checks.. Passed\e[0m\n"
fi


if [ -d htmlcov ]
then
  rm -fr htmlcov
fi
if [ -d htmlcov-unit ]
then
  rm -fr htmlcov-unit
fi
if [ -d htmlcov-unitcore ]
then
  rm -fr htmlcov-unitcore
fi
if [ -d htmlcov-integration ]
then
  rm -fr htmlcov-integration
fi

function combine_reports {
  if [ $1 = "1" ]
  then
    mv htmlcov htmlcov-unitcore
    mv .coverage .coverage-previous
  fi

  if [ $2 = "1" ]
  then
    mv htmlcov htmlcov-unit
    mv .coverage htmlcov-unitcore
    coverage combine htmlcov-unitcore/.coverage .coverage-previous
    coverage html
    mv .coverage .coverage-previous
  fi

  if [ $3 = "1" ]
  then
    mv htmlcov htmlcov-integration
    mv .coverage htmlcov-integration
    coverage combine htmlcov-integration/.coverage .coverage-previous
    coverage html
  fi
}

printf "\n\e[1;33mUnit Tests (Core Set).....\e[0m\n"
nose2 -s test/unitcore -t . -v --with-coverage --coverage-config .coveragerc --coverage-report html
if [ $? != 0 ]
then
  printf "\n\e[1;31mUnit tests.. (Core Set) Failed\e[0m\n"
  combine_reports 0 0 0 0 0 0
  exit 1;
else
  printf "\n\e[1;32mUnit tests.. (Core Set) Passed\e[0m\n"
  combine_reports 1 0 0 0 0 0
fi


printf "\n\e[1;33mUnit Tests (Extended Set).....\e[0m\n"
nose2 -s test/unit -t . -v --with-coverage --coverage-config .coveragerc --coverage-report html
if [ $? != 0 ]
then
  printf "\n\e[1;31mUnit tests.. (Extended Set) Failed\e[0m\n"
  combine_reports 0 0 0 0 0 0
  exit 1;
else
  printf "\n\e[1;32mUnit tests.. (Extended Set) Passed\e[0m\n"
  combine_reports 0 1 0 0 0 0
fi

if [ -f "/.dockerenv" ]
then
  printf "\n\e[1;33mIntegration Tests.....\e[0m\n"
else
  printf "\n\e[0;33mNot running inside docker - skipping integration tests.\e[0m\n"
  testtype="unit"
fi

if [ "$testtype" = "unit" ]
then
  printf "\n\e[0;33mRequested to only run unit tests\e[0m\n"
fi


if [ "$testtype" = "all" ]
then
  nose2 -s test/integration -t . -v --with-coverage --coverage-config .coveragerc --coverage-report html
  if [ $? != 0 ]
  then
    printf "\n\e[1;31mIntegration tests.. (Extended Set) Failed\e[0m\n"
    combine_reports 0 0 0 0 0 0
    exit 1;
  else
    printf "\n\e[1;32mIntegration tests.. (Extended Set) Passed\e[0m\n"
    combine_reports 0 0 1 0 0 0
  fi
fi

if [ "$testtype" = "all" ]
then
  pytest -vv --disable-warnings --cov-config=.coveragerc --cov-report=html --cov=./ tests/pytest_integration

  if [ $? != 0 ]
  then
    printf "\n\e[1;31mIntegration tests (pytest based).. (Extended Set) Failed\e[0m\n"
    combine_reports 0 0 0 0 0 0
    exit 1;
  else
    printf "\n\e[1;32mIntegration tests (pytest based).. (Extended Set) Passed\e[0m\n"
    combine_reports 0 0 1 0 0 0
  fi
fi

printf "\n\e[1;33mCoverage Report.....\e[0m\n"
coverage report

printf "\n\n\e[1;32mAll tests passed!!\e[0m\n"
