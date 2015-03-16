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
    """
    Find and return HTMLElement with ``<mods:mods>`` tag from the `dom`.
    """
    return dom.find("mods:mods")[0]


def add_missing_xml_attributes(dom, counter):
    """
    Add `xmlns` and `ID` attributes to ``<mods:mods>`` tag.
    """
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
    """
    "Make sure that ``<mods:placeTerm>`` has ``type="code"`` attribute.
    """
    # fix invalid type= paramater
    placeterm_tag = dom.match(
        "mods:originInfo",
        "mods:place",
        ["mods:placeTerm", {"authority": "marccountry"}]
    )
    if placeterm_tag:
        placeterm_tag[0].params["type"] = "code"


def add_uuid(dom, uuid):
    """
    Add ``<mods:identifier>`` with `uuid`.
    """
    mods_tag = get_mods_tag(dom)

    uuid_tag = dhtmlparser.HTMLElement(
        "mods:identifier",
        {"type": "uuid"},
        [dhtmlparser.HTMLElement(uuid)]
    )

    insert_tag(uuid_tag, dom.find("mods:identifier"), mods_tag)


def add_marccountry_tag(dom):
    """
    Add ``<mods:placeTerm>`` tag with proper content.
    """
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
                [dhtmlparser.HTMLElement("xr-")]
            )
        ]
    )
    insert_tag(
        marccountry_tag,
        dom.match("mods:mods", "mods:originInfo", "mods:place"),
        dom.find("mods:originInfo")[0]
    )


def add_genre(dom):
    """
    Add ``<mods:genre>`` with `electronic volume` content into
    ``<mods:originInfo``.
    """
    mods_tag = get_mods_tag(dom)

    matched_genres = [
        "electronic title",
        "electronic volume",
    ]
    genre = dom.find(
        "mods:genre",
        fn=lambda x: x.getContent().lower().strip() in matched_genres
    )

    if not genre:
        genre_tag = dhtmlparser.HTMLElement(
            "mods:genre",
            [dhtmlparser.HTMLElement("electronic volume")]
        )
        insert_tag(genre_tag, dom.find("mods:originInfo"), mods_tag)


def remove_hairs_from_tags(dom):
    """
    Use :func:`.remove_hairs` to some of the tags:

        - mods:title
        - mods:placeTerm
    """
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


def fix_issuance(dom):
    """
    Fix <mods:issuance> for monographic tags from `monographic` to
    `single_unit`.
    """
    transform_content(
        dom.match(
            "mods:originInfo",
            {
                "tag_name": "mods:issuance",
                "fn": lambda x: x.getContent() == "monographic"
            }
        ),
        lambda x: "single unit"
    )


def fix_location_tag(dom):
    """
    Repair the <mods:location> tag (the XSLT template returns things related to
    paper books, not electronic documents).
    """
    location = dom.match(
        "mods:mods",
        "mods:location",
    )

    # if no location tag found, there is nothing to be fixed
    if not location:
        return
    location = location[0]

    # fix only <mods:location> containing <mods:physicalLocation> tags
    if not location.find("mods:physicalLocation"):
        return

    url = location.find("mods:url", {"usage": "primary display"})

    # parse URL
    if url:
        url = url[0].getContent()
    else:
        urls = filter(
            lambda x: x.getContent(),
            location.find("mods:url")
        )

        if not urls:
            return

        url = max(urls, key=lambda x: len(x))

    # replace the code with new tag
    replacer = dhtmlparser.parseString("""
  <mods:location>
    <mods:holdingSimple>
      <mods:copyInformation>
        <mods:electronicLocator>%s</mods:electronicLocator>
      </mods:copyInformation>
    </mods:holdingSimple>
  </mods:location>
    """ % url)

    location.replaceWith(
        replacer.find("mods:location")[0]
    )

    dhtmlparser.makeDoubleLinked(dom)


def fix_related_item_tag(dom):
    """
    Remove <mods:relatedItem> tag in case that there is only <mods:location>
    subtag.
    """
    location = dom.match(
        "mods:mods",
        "mods:relatedItem",
        "mods:location"
    )

    if not location:
        return
    location = location[0]

    location.replaceWith(
        dhtmlparser.HTMLElement()
    )

    # remove whole <mods:relatedItem> tag, if there is nothing else left in it
    related_item = dom.match(
        "mods:mods",
        "mods:relatedItem"
    )
    related_item = related_item[0]

    if not related_item.getContent().strip():
        related_item.replaceWith(dhtmlparser.HTMLElement())


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

    fix_issuance(dom)
    fix_location_tag(dom)
    fix_related_item_tag(dom)

    return '<?xml version="1.0" encoding="UTF-8"?>\n\n' + dom.prettify()
