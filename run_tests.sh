#! /usr/bin/env bash

PYTHONPATH="$PYTHONPATH:src/edeposit/amqp"
TEST_PATH="tests"

py.test "$TEST_PATH"