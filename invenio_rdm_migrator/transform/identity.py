# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transform interfaces."""

from functools import partial

from .base import Transform


class IdentityTransform(Transform):
    """Transform class to yield the received item without change."""

    def _transform(self, entry):
        """Transform entry."""
        return entry


class IdentityDictKeyMixin:
    """Translates a function name to a dictionary key.

    Prevents unnecessary implementations where the return value of a function
    is merely the dictionary value of key with the same name as the function.
    Or as in this case, prefixed with underscore.

    .. highlight:: python
    .. code-block:: python

        def _test(data):
            return data["test"]
    """

    @staticmethod
    def unprefixed_dict_access(key, data):
        """Removes the prefix from the key and returns the value of the dict."""
        if key.startswith("_"):
            key = key[1:]

        return data[key]

    def __getattr__(self, item):
        """Fallback to the dict access when the attr/func was not found in the class."""
        # note that python will give priority to the implemented functions before calling
        # this method, the one called always is __getattribute__
        # see test_identity_dict_key_mixin for more details
        return partial(self.unprefixed_dict_access, item)
