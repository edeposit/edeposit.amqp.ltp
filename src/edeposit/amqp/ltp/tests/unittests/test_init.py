#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
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
