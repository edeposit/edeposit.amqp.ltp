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
import hashlib

from dhtmlparser import HTMLElement
import xmltodict
from edeposit.amqp.aleph import marcxml

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


def _path_to_id(path):
    if path.endswith("/"):
        path = path[:-1]

    return os.path.basename(path)


def _compose_info(root_dir, original_fn, metadata_fn, hash_fn, aleph_record):
    # compute hash for hashfile
    with open(hash_fn) as f:
        hash_file_md5 = hashlib.md5(f.read()).hexdigest()

    document = {
        "info": {
            "created": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "metadataversion": "1.0",
            "packageid": _path_to_id(root_dir),
            "mainmets": _get_localized_fn(metadata_fn, root_dir),
            "itemlist": {
                "@itemtotal": "1",
                "item": [
                    _get_localized_fn(original_fn, root_dir),
                ]
            },
            "checksum": {
                "@type": "MD5",
                "@checksum": hash_file_md5,
                "#text": hash_fn
            },
            "collection": "edeposit"
        }
    }

    # get informations from MARC record
    record = marcxml.MARCXMLRecord(aleph_record)

    # get publisher info
    if record.getPublisher(None):
        document["info"]["institution"] = record.getPublisher()

    # collect informations for <titleid> tags
    isbns = record.getISBNs()

    ccnb = marcxml._undefinedPattern(
        "".join(record.getDataRecords("015", "a", False)),
        lambda x: x.strip() == "",
        None
    )

    urnnbn = record.getDataRecords("856", "u", False)

    if any([isbns, ccnb, urnnbn]):  # issn
        document["info"]["titleid"] = []

    for isbn in isbns:
        document["info"]["titleid"].append({
            "@type": "isbn",
            "#text": isbn
        })

    if ccnb:
        document["info"]["titleid"].append({
            "@type": "ccnb",
            "#text": ccnb
        })

    if urnnbn:
        document["info"]["titleid"].append({
            "@type": "urnnbn",
            "#text": urnnbn
        })

    # if issn:
    #     document["info"]["titleid"].append({
    #         "@type": "issn",
    #         "#text": issn
    #     })

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

print _compose_info(
    "/somewhere/root_dir",
    "/somewhere/root_dir/original_fn",
    "/somewhere/root_dir/metadata_fn",
    "/proc/cpuinfo",
    open("/home/bystrousak/Plocha/prace/test/aleph/tests/resources/aleph_data_examples/aleph_sources/example4.xml").read()
)


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

    # count md5 sums
    md5_fn = os.path.join(root_dir, settings.MD5_FILENAME)
    with open(md5_fn) as f:
        f.write(
            checksum_generator.generate_hashfile(root_dir)
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
    _compose_info(md5_fn)



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