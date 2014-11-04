#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
from ltp import mods_postprocessor, xslt_transformer
import test_xslt_transformer


# Variables ===================================================================
POSTPROCESSED_FN = test_xslt_transformer.DIRNAME + "postprocessed_mods.xml"


# Tests =======================================================================
def test_postprocess_mods():
    result = xslt_transformer.transform_to_mods(test_xslt_transformer.OAI_FILENAME)

    with open(test_xslt_transformer.TRANSFORMED_FN) as f:
        assert result == f.read()

    postprocessed = mods_postprocessor.postprocess_mods(result, "someid")

    # with open("xex.xml", "wt") as f:
    #     f.write(postprocessed)

    with open(POSTPROCESSED_FN) as f:
        assert postprocessed == f.read()
