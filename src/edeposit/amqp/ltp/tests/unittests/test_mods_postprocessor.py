#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
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
