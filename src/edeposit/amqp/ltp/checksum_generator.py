#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
# Imports =====================================================================
import os
import hashlib


# Variables ===================================================================
_BLACKLIST = {
    "info.xml"
}


# Functions & objects =========================================================
def _get_required_fn(fn, root_path):
    replacer = "/" if root_path.endswith("/") else ""

    return fn.replace(root_path, replacer, 1)


def generate_checksums(directory, blacklist=_BLACKLIST):
    if not os.path.exists(directory):
        raise UserWarning("'%s' doesn't exists!" % directory)

    hashes = []
    for root, dirs, files in os.walk(directory):
        for fn in files:
            # skip files on blacklist
            if fn in blacklist:
                continue

            fn = os.path.join(root, fn)

            # compute hash of the file
            with open(fn) as f:
                fn_hash = hashlib.md5(f.read())

            # append pair (hash, fixed_fn)
            hashes.append(
                (
                    fn_hash.hexdigest(),
                    _get_required_fn(fn, directory)
                )
            )

    return hashes


print generate_checksums("/home/bystrousak/.ssh")