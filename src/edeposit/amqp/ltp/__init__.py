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
import xmltodict

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


def _get_localized_fn(fn, root_dir):
    local_fn = fn.replace(root_dir, "")

    if not local_fn.startswith("/"):
        return "/" + local_fn

    return local_fn


def _compose_info(package_id, root_dir, original_fn, metadata_fn):
    document = {
        "info": {
            "created": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "metadataversion": "1.0",
            "packageid": package_id,
            "mainmets": _get_localized_fn(metadata_fn, root_dir),
            "itemlist": {
                "@itemtotal": "1",
                "item": _get_localized_fn(original_fn, root_dir)
            }
        }
    }

    # document["info"]["titleid"] = {
    #     "@type": "isbn",
    #     "#text": isbn
    # }
    # document["info"]["titleid"] = {
    #     "@type": "issn",
    #     "#text": issn
    # }
    # document["info"]["titleid"] = {
    #     "@type": "ccnb",
    #     "#text": ccnb
    # }
    # document["info"]["titleid"] = {
    #     "@type": "urnnbn",
    #     "#text": urnnbn
    # }

    return xmltodict.unparse(document, pretty=True)


    dom = HTMLElement(
        "info",
        [
            HTMLElement("created", [HTMLElement(
                time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
            )]),
            HTMLElement("metadataversion", [HTMLElement("1.0")])
        ]
    )

    return dom.prettify()

print _compose_info("id", "root_dir", "root_dir/original_fn", "metadata_fn")


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