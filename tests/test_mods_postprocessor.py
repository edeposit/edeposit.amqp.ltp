#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import dhtmlparser

from ltp import xslt_transformer
from ltp import mods_postprocessor
from ltp.mods_postprocessor.shared_funcs import remove_hairs

import test_xslt_transformer


# Variables ===================================================================
POSTPROCESSED_FN = test_xslt_transformer.DIRNAME + "postprocessed_mods.xml"


# Tests =======================================================================
def test_remove_hairs():
    assert remove_hairs(",a-sd,-/") == "a-sd"


def test_postprocess_mods():
    result = xslt_transformer.transform_to_mods(
        test_xslt_transformer.OAI_FILENAME,
        "someid"
    )

    # with open("xex.xml", "wt") as f:
        # f.write(result[0])

    with open(POSTPROCESSED_FN) as f:
        assert result[0] == f.read()


def test_fix_location_tag():
    XML = """
<mods:mods>
  <mods:identifier type="ccnb">cnb000003024</mods:identifier>
  <mods:location>
    <mods:physicalLocation authority="siglaADR">ABA001</mods:physicalLocation>
    <mods:url displayLabel="electronic resource" usage="primary display">http://edeposit-test.nkp.cz/producents/beta-nakladatelstvi/epublications/controlling-v-msp-nejen-o-cislech/controlling.pdf</mods:url>
    <mods:url displayLabel="electronic resource">http://edeposit.nkp.cz/</mods:url>
  </mods:location>
  <mods:identifier type="uuid">236b6283-22d1-4014-ae50-a303cfd15419</mods:identifier>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
  <mods:relatedItem>
    <mods:location>
      <mods:url>http://edeposit.nkp.cz/</mods:url>
    </mods:location>
  </mods:relatedItem>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
</mods:mods>
    """

    dom = dhtmlparser.parseString(XML)
    dhtmlparser.makeDoubleLinked(dom)

    mods_postprocessor.monograph.fix_location_tag(dom)

    assert dom.__str__() == """
<mods:mods>
  <mods:identifier type="ccnb">cnb000003024</mods:identifier>
  <mods:location>
    <mods:holdingSimple>
      <mods:copyInformation>
        <mods:electronicLocator>http://edeposit-test.nkp.cz/producents/beta-nakladatelstvi/epublications/controlling-v-msp-nejen-o-cislech/controlling.pdf</mods:electronicLocator>
      </mods:copyInformation>
    </mods:holdingSimple>
  </mods:location>
  <mods:identifier type="uuid">236b6283-22d1-4014-ae50-a303cfd15419</mods:identifier>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
  <mods:relatedItem>
    <mods:location>
      <mods:url>http://edeposit.nkp.cz/</mods:url>
    </mods:location>
  </mods:relatedItem>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
</mods:mods>
    """


def test_fix_related_item_tag():
    XML = """
<mods:mods>
  <mods:identifier type="ccnb">cnb000003024</mods:identifier>
  <mods:identifier type="uuid">236b6283-22d1-4014-ae50-a303cfd15419</mods:identifier>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
  <mods:relatedItem>
    <mods:location>
      <mods:url>http://edeposit.nkp.cz/</mods:url>
    </mods:location>
  </mods:relatedItem>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
</mods:mods>
    """

    dom = dhtmlparser.parseString(XML)
    dhtmlparser.makeDoubleLinked(dom)

    mods_postprocessor.monograph.fix_related_item_tag(dom)

    assert dom.prettify() == """<mods:mods>
  <mods:identifier type="ccnb">cnb000003024</mods:identifier>
  <mods:identifier type="uuid">236b6283-22d1-4014-ae50-a303cfd15419</mods:identifier>
  <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
    <mods:identifier type="isbn">978-80-7408-086-9</mods:identifier>
</mods:mods>
"""