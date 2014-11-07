#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser


# Functions & objects =========================================================
def _remove_hairs(inp, hairs="/:;,- []<>()"):
    """
    Remove "special" characters from beginning and the end of the `inp`. For
    example ``,a-sd,-/`` -> ``a-sd``.

    Args:
        inp (str): Input string.

    Returns:
        str: Cleaned string.
    """
    while inp and inp[-1] in hairs:
        inp = inp[:-1]

    while inp and inp[0] in hairs:
        inp = inp[1:]

    return inp


def insert_tag(tag, before, root):
    """
    Insert `tag` before `before` tag if present. If not, insert it into `root`.

    Args:
        tag (obj): HTMLElement instance.
        before (obj): HTMLElement instance.
        root (obj): HTMLElement instance.
    """
    if not before:
        root.childs.append(tag)
        tag.parent = root
        return

    before = before[0] if type(before) in [tuple, list] else before

    # put it before first existing identifier
    parent = before.parent
    parent.childs.insert(
        parent.childs.index(before),
        tag
    )
    tag.parent = parent


def transform_content(tags, content_transformer):
    """
    Transform content in all `tags` using result of `content_transformer(tag)`
    call.

    Args:
        tags (obj/list): HTMLElement instance, or list of HTMLElement
                         instances.
        content_transformer (function): Function which is called as
                                        ``content_transformer(tag)``.
    """
    if type(tags) not in [tuple, list]:
        tags = [tags]

    for tag in tags:
        tag.childs = [
            dhtmlparser.HTMLElement(content_transformer(tag))
        ]


def postprocess_mods(mods, package_id=None):
    """
    Fix bugs in `mods` produced by XSLT template.

    Args:
        mods (str): XML string generated by XSLT template.
        package_id (str, default None): UUID of the package.

    Returns:
        str: Updated XML.
    """
    dom = dhtmlparser.parseString(mods)
    dhtmlparser.makeDoubleLinked(dom)

    # add missing parameter
    mods_tag = dom.find("mods:mods")
    if mods_tag:
        mods_tag[0].params["ID"] = "MODS_TITLE_0001"

    # fix invalid type= paramater
    placeterm_tag = dom.match(
        "mods:originInfo",
        "mods:place",
        ["mods:placeTerm", {"authority": "marccountry"}]
    )
    if placeterm_tag:
        placeterm_tag[0].params["type"] = "code"

    # add identifier to the section with identifiers
    if package_id:
        uuid_tag = dhtmlparser.HTMLElement(
            "mods:identifier",
            {"type": "uuid"},
            [dhtmlparser.HTMLElement(package_id)]
        )
        insert_tag(uuid_tag, dom.find("mods:identifier"), mods_tag)

    # add marccountry if not found
    marccountry = dom.find("mods:placeTerm", {"authority": "marccountry"})
    if not marccountry:
        marccountry_tag = dhtmlparser.HTMLElement(
            "mods:place",
            [
                dhtmlparser.HTMLElement(
                    "mods:placeterm",
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

    # add <genre> tag if not found
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

    # remove hairs from some tags
    transform_content(
        dom.match("mods:mods", "mods:titleInfo", "mods:title"),
        lambda x: _remove_hairs(x.getContent())
    )
    transform_content(
        dom.match(
            "mods:originInfo",
            "mods:place",
            ["mods:placeTerm", {"type": "text"}]
        ),
        lambda x: _remove_hairs(x.getContent())
    )

    return dom.prettify()
