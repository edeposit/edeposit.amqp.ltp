#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import time
import shutil
import base64
import os.path

from dhtmlparser import HTMLElement

import settings
import structures

import xslt_transformer
import checksum_generator


# Variables ===================================================================


# Functions & objects =========================================================
def _get_package_name():
    return os.path.join(settings.TEMP_DIR, "dokument/")  # TODO


def _get_suffix(fn):
    suffix = fn.split(".")[-1]

    if "/" in suffix:
        raise UserWarning("Filename can't contain '/' in suffix (%s)!" % fn)

    return suffix


def _get_original_fn(book_id, ebook_fn):
    return "oc_nk-edep-" + str(book_id) + "." + _get_suffix(ebook_fn)


def _get_metadata_fn(book_id):
    return "meds_nk-edep-" + str(book_id) + ".xml"


def _create_package_hierarchy():
    root_dir = _get_package_name()

    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)

    os.mkdir(root_dir)

    original_dir = os.path.join(root_dir, "original")
    metadata_dir = os.path.join(root_dir, "metadata")

    os.mkdir(original_dir)
    os.mkdir(metadata_dir)

    return root_dir, original_dir, metadata_dir


def _compose_info(root_dir, original_fn, metadata_fn):
    dom = HTMLElement(
        "info",
        [
            HTMLElement("created", [HTMLElement(
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            )])
        ]
    )

    return str(dom)


def create_ltp_package(aleph_record, book_id, ebook_fn, b64_data):
    root_dir, original_dir, metadata_dir = _create_package_hierarchy()

    # create original file
    original_fn = os.path.join(
        original_dir,
        _get_original_fn(book_id, ebook_fn)
    )
    with open(original_fn, "wb") as f:
        f.write(
            base64.b64decode(b64_data)
        )

    # create metadata file
    metadata_fn = os.path.join(
        metadata_dir,
        _get_metadata_fn(book_id)
    )
    with open(metadata_fn, "w") as f:
        f.write(
            xslt_transformer.transform_to_mods(aleph_record)
        )

    # create info file




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
        object: Response class from :mod:`structures`.

    Raises:
        ValueError: if bad type of `message` structure is given.
    """
    pass