# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Ignored actions module."""

from ....actions import LoadAction


class AnyData:
    """Utility class for accepting any combination of data arguments."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        pass


class IgnoredAction(LoadAction):
    """Ingored action.

    This is a utility class used in case there are actions that need to be parsed, but
    are ignored/skipped and do not translate to a set of generate rows.
    """

    name = "ignored"
    data_cls = AnyData

    def _generate_rows(self, **kwargs):
        """Yields nothing."""
        yield from iter(())
