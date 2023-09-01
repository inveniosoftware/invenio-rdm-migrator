# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration GitHub table load module."""

from ...load.postgresql.bulk.generators import TableGenerator
from ...state import STATE
from ..models.github import Release


class ReleaseTableGenerator(TableGenerator):
    """GitHub release table load."""

    def __init__(self):
        """Constructor."""
        super().__init__(tables=[Release], pks=[])

    def _generate_rows(self, data, **kwargs):
        recid = data.pop("recid", None)
        release = dict(**data)
        if recid:
            record = STATE.RECORDS.get(str(recid))
            release["record_id"] = record["id"]
        yield Release(**release)
