#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from shared_funcs import insert_tag
from shared_funcs import remove_hairs
from shared_funcs import transform_content


# Functions & objects =========================================================
def get_mods_tag(dom):
    return dom.find("mods:mods")[0]


def add_missing_xml_attributes(dom, counter):
    mods_tag = get_mods_tag(dom)

    if mods_tag:
        params = mods_tag.params

        # add missing attributes
        params["ID"] = "MODS_VOLUME_%04d" % (counter + 1)
        params["xmlns:mods"] = "http://www.loc.gov/mods/v3"
        params["xmlns:xlink"] = "http://www.w3.org/1999/xlink"
        params["xmlns:xsi"] = "http://www.w3.org/2001/XMLSchema-instance"
        params["xsi:schemaLocation"] = (
            "http://www.w3.org/2001/XMLSchema-instance "
            "http://www.w3.org/2001/XMLSchema.xsd "
            "http://www.loc.gov/mods/v3 "
            "http://www.loc.gov/standards/mods/v3/mods-3-4.xsd "
            "http://www.w3.org/1999/xlink http://www.w3.org/1999/xlink.xsd"
        )


def fix_invalid_type_parameter(dom):
    # fix invalid type= paramater
    placeterm_tag = dom.match(
        "mods:originInfo",
        "mods:place",
        ["mods:placeTerm", {"authority": "marccountry"}]
    )
    if placeterm_tag:
        placeterm_tag[0].params["type"] = "code"


def add_uuid(dom, uuid):
    mods_tag = get_mods_tag(dom)

    uuid_tag = dhtmlparser.HTMLElement(
        "mods:identifier",
        {"type": "uuid"},
        [dhtmlparser.HTMLElement(uuid)]
    )

    insert_tag(uuid_tag, dom.find("mods:identifier"), mods_tag)


def add_marccountry_tag(dom):
    marccountry = dom.find("mods:placeTerm", {"authority": "marccountry"})

    # don't add again if already defined
    if marccountry:
        return

    marccountry_tag = dhtmlparser.HTMLElement(
        "mods:place",
        [
            dhtmlparser.HTMLElement(
                "mods:placeTerm",
                {"type": "code", "authority": "marccountry"},
                [dhtmlparser.HTMLElement("xr")]
            )
        ]
    )
    insert_tag(
        marccountry_tag,
        dom.match("mods:mods", "mods:originInfo", "mods:place"),
        dom.find("mods:originInfo")[0]
    )


def add_genre(dom):
    mods_tag = get_mods_tag(dom)

    genre = dom.find(
        "mods:genre",
        fn=lambda x: x.getContent().lower().strip() == "electronic title"
    )

    if not genre:
        genre_tag = dhtmlparser.HTMLElement(
            "mods:genre",
            [dhtmlparser.HTMLElement("electronic title")]
        )
        insert_tag(genre_tag, dom.find("mods:originInfo"), mods_tag)


def remove_hairs_from_tags(dom):
    transform_content(
        dom.match("mods:mods", "mods:titleInfo", "mods:title"),
        lambda x: remove_hairs(x.getContent())
    )
    transform_content(
        dom.match(
            "mods:originInfo",
            "mods:place",
            ["mods:placeTerm", {"type": "text"}]
        ),
        lambda x: remove_hairs(x.getContent())
    )


def postprocess_monograph(mods, uuid, counter):
    """
    Fix bugs in `mods` produced by XSLT template.

    Args:
        mods (str): XML string generated by XSLT template.
        uuid (str): UUID of the package.

    Returns:
        str: Updated XML.
    """
    # do not parse already parsed dom's
    dom = mods
    if not isinstance(mods, dhtmlparser.HTMLElement):
        dom = dhtmlparser.parseString(mods)

    dhtmlparser.makeDoubleLinked(dom)

    add_missing_xml_attributes(dom, counter)

    fix_invalid_type_parameter(dom)

    if uuid:
        add_uuid(dom, uuid)

    add_marccountry_tag(dom)

    # add <genre> tag if not found
    add_genre(dom)

    # remove hairs from some tags
    remove_hairs_from_tags(dom)

    return '<?xml version="1.0" encoding="UTF-8"?>\n\n' + dom.prettify()