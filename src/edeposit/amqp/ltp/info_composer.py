#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import time
import os.path
import hashlib
from collections import OrderedDict

import xmltodict
from edeposit.amqp.aleph import marcxml

from mods_postprocessor.shared_funcs import remove_hairs


# Functions & classes =========================================================
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


def _add_order(inp_dict):
    """
    Add order to unordered dict.

    Order is taken from *priority table*, which is just something I did to
    make outputs from `xmltodict` look like examples in specification.

    Args:
        inp_dict (dict): Unordered dictionary.

    Returns:
        OrderedDict: Dictionary ordered by *priority table*.
    """
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
    priority_table = dict(  # construct dict keys -> {key: order}
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


def compose_info(root_dir, files, hash_fn, aleph_record):
    """
    Compose `info` XML file.

    Info example::

        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <info>
            <created>2014-07-31T10:58:53</created>
            <metadataversion>1.0</metadataversion>
            <packageid>c88f5a50-7b34-11e2-b930-005056827e51</packageid>
            <mainmets>mets.xml</mainmets>
            <titleid type="ccnb">cnb001852189</titleid>
            <titleid type="isbn">978-80-85979-89-6</titleid>
            <collection>edeposit</collection>
            <institution>nakladatelství Altar</institution>
            <creator>ABA001</creator>
            <size>1530226</size>
            <itemlist itemtotal="1">
                <item>\data\Denik_zajatce_Sramek_CZ_v30f-font.epub</item>
            </itemlist>
            <checksum type="MD5" checksum="ce076548eaade33888005de5d4634a0d">
                \MD5.md5
            </checksum>
        </info>

    Args:
        root_dir (str): Absolute path to the root directory.
        original_fn (str): Absolute path to the ebook file.
        metadata_fn (str): Absolute path to the metadata file.
        hash_fn (str): Absolute path to the MD5 file.
        aleph_record (str): String with Aleph record with metadata.

    Returns:
        str: XML string.
    """
    # compute hash for hashfile
    with open(hash_fn) as f:
        hash_file_md5 = hashlib.md5(f.read()).hexdigest()

    schema_location = "http://www.ndk.cz/standardy-digitalizace/info11.xsd"
    document = {
        "info": {
            "@xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "@xsi:noNamespaceSchemaLocation": schema_location,
            "created": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
            "metadataversion": "1.0",
            "packageid": _path_to_id(root_dir),
            "mainmets": "",

            # not used in SIP
            # "mainmets": _get_localized_fn(metadata_fn, root_dir),

            "itemlist": {
                "@itemtotal": "2",
                "item": map(
                    lambda x: _get_localized_fn(x, root_dir),
                    files
                )
            },
            "checksum": {
                "@type": "MD5",
                "@checksum": hash_file_md5,
                "#text": _get_localized_fn(hash_fn, root_dir)
            },
            "collection": "edeposit",
            "size": _calc_dir_size(root_dir) / 1024,  # size in kiB
        }
    }

    # get informations from MARC record
    record = marcxml.MARCXMLRecord(aleph_record)

    # get publisher info
    publisher = unicode(record.getPublisher(), "utf-8")
    if record.getPublisher(None):
        document["info"]["institution"] = remove_hairs(publisher)

    # get <creator> info
    creator = record.getDataRecords("910", "a", False)
    alt_creator = record.getDataRecords("040", "d", False)
    document["info"]["creator"] = creator[0] if creator else alt_creator[-1]

    # collect informations for <titleid> tags
    isbns = record.getISBNs()

    ccnb = record.getDataRecords("015", "a", False)
    ccnb = ccnb[0] if ccnb else None

    if any([isbns, ccnb]):  # TODO: issn
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

    # TODO: later
    # if issn:
    #     document["info"]["titleid"].append({
    #         "@type": "issn",
    #         "#text": issn
    #     })

    document["info"] = _add_order(document["info"])
    xml_document = xmltodict.unparse(document, pretty=True)

    # return xml_document.replace("<?xml ", '<?xml standalone="yes" ')
    return xml_document.encode("utf-8")
