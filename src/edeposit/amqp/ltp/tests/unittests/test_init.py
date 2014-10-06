#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import shutil
import os.path

import ltp


# Variables ===================================================================



# Functions & objects =========================================================


# Tests =======================================================================
def test_get_suffix():
    assert ltp._get_suffix("/home/xex/somefile.txt") == "txt"
    assert ltp._get_suffix("somefile.txt") == "txt"
    assert ltp._get_suffix("/somefile.txt") == "txt"
    assert ltp._get_suffix("somefile") == "somefile"
    assert ltp._get_suffix("/home/xex/somefile") == "somefile"


def test_get_original_fn():
    assert ltp._get_original_fn("111", "somebook.epub") == "oc_nk-edep-111.epub"
    assert ltp._get_original_fn(111, "somebook.pdf") == "oc_nk-edep-111.pdf"


def test_get_metadata_fn():
    assert ltp._get_metadata_fn("111") == "meds_nk-edep-111.xml"
    assert ltp._get_metadata_fn(111) == "meds_nk-edep-111.xml"


def test_create_package_hierarchy():
    root_dir, original_dir, metadata_dir = ltp._create_package_hierarchy("/tmp")

    assert root_dir.startswith("/tmp")

    assert original_dir.startswith(root_dir)
    assert metadata_dir.startswith(root_dir)

    assert original_dir != metadata_dir

    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)


def test_get_localized_fn():
    local_path = ltp._get_localized_fn("/home/xex/somefile.txt", "/home")
    assert local_path == "/xex/somefile.txt"

    local_path = ltp._get_localized_fn("/somefile.txt", "/")
    assert local_path == "/somefile.txt"

    local_path = ltp._get_localized_fn("/xex/somefile.txt", "/home")
    assert local_path == "/xex/somefile.txt"

    local_path = ltp._get_localized_fn("/home/xex/home/somefile.txt", "/home")
    assert local_path == "/xex/home/somefile.txt"

    local_path = ltp._get_localized_fn("somefile.txt", "/azgabash")
    assert local_path == "/somefile.txt"


def test_path_to_id():
    assert ltp._path_to_id("/xex/xax") == "xax"
    assert ltp._path_to_id("/xex/xax/") == "xax"

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
    assert ltp._calc_dir_size(root_dir) >= 3*1024

    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
