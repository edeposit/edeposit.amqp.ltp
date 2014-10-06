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
from collections import OrderedDict

import xmltodict
from edeposit.amqp.aleph import marcxml

import settings
import structures

import xslt_transformer
import checksum_generator


# Variables ===================================================================


# Functions & objects =========================================================
def _get_package_name(prefix=settings.TEMP_DIR):
    return os.path.join(prefix, "dokument/")  # TODO


def _get_suffix(path):
    """
    Return suffix from `path`.

    ``/home/xex/somefile.txt`` --> ``txt``.

    Args:
        path (str): Full file path.

    Returns:
        str: Suffix.

    Raises:
        UserWarning: When / is detected in suffix.
    """
    suffix = os.path.basename(path).split(".")[-1]

    if "/" in suffix:
        raise UserWarning("Filename can't contain '/' in suffix (%s)!" % path)

    return suffix


def _get_original_fn(book_id, ebook_fn):
    """
    Construct original filename from `book_id` and `ebook_fn`.

    Args:
        book_id (int/str): ID of the book, without special characters.
        ebook_fn (str): Original name of the ebook. Used to get suffix.

    Returns:
        str: Filename in format ``oc_nk-edep-BOOKID.suffix``.
    """
    return "oc_nk-edep-" + str(book_id) + "." + _get_suffix(ebook_fn)


def _get_metadata_fn(book_id):
    """
    Construct filename for metadata file.

    Args:
        book_id (int/str): ID of the book, without special characters.

    Returns:
        str: Filename in format ``"meds_nk-edep-BOOKID.xml``.
    """
    return "meds_nk-edep-" + str(book_id) + ".xml"


def _create_package_hierarchy(prefix=settings.TEMP_DIR):
    """
    Create hierarchy of directories, at it is required in specification.

    `root_dir` is root of the package generated using :attr:`settings.TEMP_DIR`
    and :func:`_get_package_name`.

    `original_dir` is path to the directory, where the data files are stored.

    `metadata_dir` is path to the directory with MODS metadata.

    Args:
        prefix (str): Path to the directory where the `root_dir` will be
                      stored.

    Warning:
        If the `root_dir` exists, it is REMOVED!

    Returns:
        list of str: root_dir, original_dir, metadata_dir
    """
    root_dir = _get_package_name(prefix)

    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)

    os.mkdir(root_dir)

    original_dir = os.path.join(root_dir, "original")
    metadata_dir = os.path.join(root_dir, "metadata")

    os.mkdir(original_dir)
    os.mkdir(metadata_dir)

    return root_dir, original_dir, metadata_dir


def _get_localized_fn(path, root_dir):
    """
    Return absolute `path` relative to `root_dir`.

    When `path` == ``/home/xex/somefile.txt`` and `root_dir` == ``/home``,
    returned path will be ``/xex/somefile.txt``.

    Args:
        path (str): Absolute path beginning in `root_dir`.
        root_dir (str): Absolute path containing `path` argument.

    Returns:
        str: Local `path` when `root_dir` is considered as root of FS.
    """
    local_fn = path
    if path.startswith(root_dir):
        local_fn = path.replace(root_dir, "", 1)

    if not local_fn.startswith("/"):
        return "/" + local_fn

    return local_fn


def _path_to_id(path):
    """
    Name of the root directory is used as ``<packageid>`` in ``info.xml``.

    This function makes sure, that :func:`os.path.basename` doesn't return
    blank string in case that there is `/` at the end of the `path`.

    Args:
        path (str): Path to the root directory.

    Returns:
        str: Basename of the `path`.
    """
    if path.endswith("/"):
        path = path[:-1]

    return os.path.basename(path)


def _calc_dir_size(path):
    """
    Calculate size of all files in `path`.

    Args:
        path (str): Path to the directory.

    Returns:
        int: Size of the directory in bytes.
    """
    dir_size = 0
    for (root, dirs, files) in os.walk(path):
        for fn in files:
            full_fn = os.path.join(root, fn)
            dir_size += os.path.getsize(full_fn)

    return dir_size


def _remove_hairs(inp):
    special_chars = "/:;,- []<>()"

    while inp and inp[-1] in special_chars:
        inp = inp[:-1]

    while inp and inp[1:] in special_chars:
        inp = inp[1:]

    return inp


def _add_order(inp_dict):
    out = OrderedDict()

    priority_table = [
        "created",
        "metadataversion",
        "packageid",
        "mainmets",
        "titleid",
        "collection",
        "institution",
        "creator",
        "size",
        "itemlist",
        "checksum"
    ]
    priority_table = dict(
        map(
            lambda (cnt, key): (key, cnt),
            enumerate(priority_table)
        )
    )

    sorted_keys = sorted(
        inp_dict.keys(),
        key=lambda x: priority_table.get(x, x)
    )
    for key in sorted_keys:
        out[key] = inp_dict[key]

    return out


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
            "collection": "edeposit",
            "size": _calc_dir_size(root_dir) / 1024,  # size in kiB
        }
    }

    # get informations from MARC record
    record = marcxml.MARCXMLRecord(aleph_record)

    # get publisher info
    if record.getPublisher(None):
        document["info"]["institution"] = _remove_hairs(
            record.getPublisher()
        )

    # get <creator> info
    creator = record.getDataRecords("910", "a", False)
    alt_creator = record.getDataRecords("040", "d", False)
    document["info"]["creator"] = creator[0] if creator else alt_creator[-1]

    # collect informations for <titleid> tags
    isbns = record.getISBNs()

    ccnb = record.getDataRecords("015", "a", False)
    ccnb = ccnb[0] if ccnb else None

    urnnbn = record.getDataRecords("856", "u", False)
    urnnbn = urnnbn[0] if urnnbn else None

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

    # TODO: later
    # if issn:
    #     document["info"]["titleid"].append({
    #         "@type": "issn",
    #         "#text": issn
    #     })

    document["info"] = _add_order(document["info"])
    xml_document = xmltodict.unparse(document, pretty=True)

    return xml_document.replace("<?xml ", '<?xml standalone="yes" ')


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
    with open(os.path.join(root_dir, settings.INFO_FILENAME), "w") as f:
        f.write(
            _compose_info(
                root_dir,
                original_fn,
                metadata_fn,
                md5_fn,
                aleph_record,
            )
        )


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