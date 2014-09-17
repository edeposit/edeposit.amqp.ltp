#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os.path
import StringIO
import lxml.etree as ET


# Variables ===================================================================


# Functions & objects =========================================================
def _read_marcxml(marc_xml):  # TODO: konverze marc OAI na marc XML
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
