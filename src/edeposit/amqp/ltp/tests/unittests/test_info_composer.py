#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import shutil
import os.path

import dhtmlparser

import ltp.ltp as ltp
import ltp.info_composer as icp


# Variables ===================================================================
# Variables ===================================================================
DIRNAME = os.path.dirname(__file__) + "/data/"
OAI_FILENAME = DIRNAME + "oai_example.oai"
HASH_FILE = DIRNAME + "hashfile.md5"


# Tests =======================================================================
def test_get_localized_fn():
    local_path = icp._get_localized_fn("/home/xex/somefile.txt", "/home")
    assert local_path == "/xex/somefile.txt"

    local_path = icp._get_localized_fn("/somefile.txt", "/")
    assert local_path == "/somefile.txt"

    local_path = icp._get_localized_fn("/xex/somefile.txt", "/home")
    assert local_path == "/xex/somefile.txt"

    local_path = icp._get_localized_fn("/home/xex/home/somefile.txt", "/home")
    assert local_path == "/xex/home/somefile.txt"

    local_path = icp._get_localized_fn("somefile.txt", "/azgabash")
    assert local_path == "/somefile.txt"


def test_path_to_id():
    assert icp._path_to_id("/xex/xax") == "xax"
    assert icp._path_to_id("/xex/xax/") == "xax"

    assert os.path.basename("/xex/xax/") == ""


def test_calc_dir_size():
    root_dir, original_dir, metadata_dir = ltp._create_package_hierarchy("/tmp")

    # create 3 files
    with open(os.path.join(root_dir, "root_file.txt"), "w") as f:
        f.write(1024 * "f")

    with open(os.path.join(original_dir, "original_file.txt"), "w") as f:
        f.write(1024 * "f")

    with open(os.path.join(metadata_dir, "meta_file.txt"), "w") as f:
        f.write(1024 * "f")

    # compute size of the files
    assert icp._calc_dir_size(root_dir) >= 3*1024

    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)


def test_add_order():
    unordered = {
        "size": 1,
        "created": 1,
        "creator": 1,
        "titleid": 1,
        "itemlist": 1,
        "collection": 1,
        "checksum": 1,
        "packageid": 1,
        "institution": 1,
        "metadataversion": 1,
        "something_random": "yey"
    }

    ordered = icp._add_order(unordered)

    assert ordered.keys() == [
        "created",
        "metadataversion",
        "packageid",
        "titleid",
        "collection",
        "institution",
        "creator",
        "size",
        "itemlist",
        "checksum",
        "something_random"
    ]


def test_compose_info():
    info_xml = icp.compose_info(
        "/home/root_dir",
        [
            "/home/root_dir/data/ebook.epub",
            "/home/root_dir/meta/meta.xml",
        ],
        HASH_FILE,
        open(OAI_FILENAME).read()
    )

    dom = dhtmlparser.parseString(info_xml.encode("utf-8"))

    assert ":" in dom.find("created")[0].getContent()
    assert "-" in dom.find("created")[0].getContent()
    assert "T" in dom.find("created")[0].getContent()
    assert len(dom.find("created")[0].getContent()) >= 19
    assert dom.find("metadataversion")[0].getContent() == "1.0"
    assert dom.find("packageid")[0].getContent() == "root_dir"
    assert dom.find("titleid")[0].getContent() == "80-251-0225-4"
    assert dom.find("titleid")[1].getContent() == "cnb001492461"
    assert dom.find("collection")[0].getContent() == "edeposit"
    assert dom.find("institution")[0].getContent() == "Computer Press"
    assert dom.find("creator")[0].getContent() == "ABA001"
    assert dom.find("size")[0].getContent() == "0"
    assert dom.find("itemlist")[0].find("item")[0].getContent() == "/data/ebook.epub"
    assert dom.find("checksum")[0].getContent().endswith("hashfile.md5")
    assert dom.find("checksum")[0].params["checksum"] == "18c0864b36d60f6036bf8eeab5c1fe7d"
