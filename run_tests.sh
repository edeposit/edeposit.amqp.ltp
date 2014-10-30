#! /usr/bin/env bash

PYTHONPATH="$PYTHONPATH:src/edeposit/amqp"
TEST_PATH="src/edeposit/amqp/ltp/tests"

py.test "$TEST_PATH/unittests"