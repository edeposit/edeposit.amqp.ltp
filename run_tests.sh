#! /usr/bin/env bash
PYTHONPATH="src/edeposit/amqp$PYTHONPATH"

py.test tests $@
