#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path
import StringIO
import lxml.etree as ET


import dhtmlparser


# Variables ===================================================================


# Functions & objects =========================================================
def _add_namespace(marc_xml):
    dom = dhtmlparser.parseString(marc_xml)

    for col in dom.find("collection"):
        col.params["xmlns"] = "http://www.loc.gov/MARC21/slim"
        col.params["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        col.params["xsi:schemaLocation"] = "http://www.loc.gov/MARC21/slim " + \
                  "http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd"

    dom.find("root")[0].params = {}

    return str(dom)


def _read_marcxml(marc_xml):  # TODO: konverze marc OAI na marc XML
    marc_xml = _add_namespace(marc_xml)
    file_obj = StringIO.StringIO(marc_xml)

    return ET.parse(file_obj)


def _read_template_file(template_fn):
    if not os.path.exists(template_fn):
        raise UserWarning("'%s' doesn't exists!" % template_fn)

    return ET.parse(template_fn)


def transform(marc_xml, template_fn):
    transformer = ET.XSLT(
        _read_template_file(template_fn)
    )
    newdom = transformer(
        _read_marcxml(marc_xml)
    )

    return ET.tostring(newdom, pretty_print=True)

print transform(open("/home/bystrousak/Plocha/LTP/aleph_example.xml").read(), "xslt/MARC21slim2MODS3-4-NDK.xsl")