#! /usr/bin/env bash
export PYTHONPATH="src/edeposit/amqp:$PYTHONPATH"

py.test tests $@
