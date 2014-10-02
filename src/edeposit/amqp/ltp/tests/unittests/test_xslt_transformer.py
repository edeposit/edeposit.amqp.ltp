#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import os.path
import lxml.etree as ET

import dhtmlparser

from ltp import xslt_transformer


# Variables ===================================================================
DIRNAME = os.path.dirname(__file__) + "/data/"
OAI_FILENAME = DIRNAME + "oai_example.oai"
CONVERTED_MARC_FN = DIRNAME + "converted_oai.xml"
XSLT_FILENAME = DIRNAME + "MARC21slim2MODS3-4-NDK.xsl"


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
    xml = "<root xex=1><record xex=1 /></root>"
    fixed_xml = xslt_transformer._add_namespace(xml)

    dom = dhtmlparser.parseString(fixed_xml)

    root = dom.find("root")[0]
    assert root.params == {}

    record = dom.find("record")[0]
    assert record.params == {}

    collection = dom.find("collection")[0]
    assert collection.params
    assert "xmlns" in collection.params
    assert "xmlns:xsi" in collection.params
    assert "xsi:schemaLocation" in collection.params

    assert dom.match("collection", "record")


def test_add_namespace_collection_params():
    xml = "<collection xmlns=1><record xex=1 /></collection>"
    fixed_xml = xslt_transformer._add_namespace(xml)

    dom = dhtmlparser.parseString(fixed_xml)

    record = dom.find("record")[0]
    assert record.params == {}

    collection = dom.find("collection")[0]
    assert collection.params
    assert "xmlns" in collection.params
    assert "http" in collection.params["xmlns"]
    assert "xmlns:xsi" in collection.params
    assert "xsi:schemaLocation" in collection.params

    assert dom.match("collection", "record")


def test_read_marcxml():
    with open(OAI_FILENAME) as f:
        oai_xml = f.read()

    marc_xml = xslt_transformer._read_marcxml(oai_xml)

    assert isinstance(marc_xml, ET._ElementTree)

    marc_xml = ET.tostring(marc_xml)

    assert marc_xml
    assert "<record" in marc_xml
    assert "<datafield" in marc_xml
    assert "<subfield" in marc_xml


def test_read_marcxml_fn():
    marc_xml = xslt_transformer._read_marcxml(OAI_FILENAME)

    assert isinstance(marc_xml, ET._ElementTree)

    marc_xml = ET.tostring(marc_xml)

    assert marc_xml
    assert "<record" in marc_xml
    assert "<datafield" in marc_xml
    assert "<subfield" in marc_xml


def test_read_template():
    with open(XSLT_FILENAME) as f:
        xslt_xml = f.read()

    xslt = xslt_transformer._read_template(xslt_xml)

    assert isinstance(xslt, ET._ElementTree)

    xslt_str = ET.tostring(xslt)

    assert xslt_str
    assert "<xsl:stylesheet" in xslt_str
    assert "<xsl:output" in xslt_str
    assert "</xsl:stylesheet>" in xslt_str


def test_read_template_fn():
    xslt = xslt_transformer._read_template(XSLT_FILENAME)

    assert isinstance(xslt, ET._ElementTree)

    xslt_str = ET.tostring(xslt)

    assert xslt_str
    assert "<xsl:stylesheet" in xslt_str
    assert "<xsl:output" in xslt_str
    assert "</xsl:stylesheet>" in xslt_str


def test_transform():
    pass

def test_transform_to_mods():
    pass
