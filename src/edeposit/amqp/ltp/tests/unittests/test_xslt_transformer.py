#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import os.path

from ltp import xslt_transformer


# Variables ===================================================================
DIRNAME = os.path.dirname(__file__) + "/data/"
OAI_FILENAME = DIRNAME + "oai_example.oai"
CONVERTED_MARC_FN = DIRNAME + "converted_oai.xml"


# Functions & objects =========================================================
def test_oai_to_xml():
    with open(OAI_FILENAME) as f:
        oai_content = f.read()

    assert oai_content

    marc_xml = xslt_transformer.oai_to_xml(oai_content)

    assert marc_xml
    assert "<record" in marc_xml
    assert "<datafield" in marc_xml
    assert "<subfield" in marc_xml

    with open(CONVERTED_MARC_FN) as f:
        assert marc_xml == f.read()


def test_add_namespace():
    pass

def test_read_marcxml():
    pass

def test_read_template():
    pass

def test_transform():
    pass