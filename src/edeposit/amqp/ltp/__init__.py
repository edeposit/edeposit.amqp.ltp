#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import settings
import structures

import ltp


# Functions & objects =========================================================
def _instanceof(instance, cls):
    """
    Check type of `instance` by matching ``.__name__`` with `cls.__name__`.
    """
    return type(instance).__name__ == cls.__name__


# Main program ================================================================
def reactToAMQPMessage(message, UUID):
    """
    React to given (AMQP) message. `message` is expected to be
    :py:func:`collections.namedtuple` structure from :mod:`.structures` filled
    with all necessary data.

    Args:
        message (object): One of the request objects defined in
                          :mod:`.structures`.
        UUID (str): Unique ID of received message.

    Returns:
        object: Response class from :mod:`.structures`.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    pass