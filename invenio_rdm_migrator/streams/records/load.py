# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record load module."""

from ...load import PostgreSQLCopyLoad
from ..cache import ParentsCache, RecordsCache
from .table_generators import (
    RDMDraftTableGenerator,
    RDMRecordTableGenerator,
    RDMVersionStateTableGenerator,
)


class RDMRecordCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL COPY load."""

    def __init__(self, cache, db_uri, tmp_dir):
        """Constructor."""
        self.parents_cache = cache.get("parents", ParentsCache())
        self.records_cache = cache.get("records", RecordsCache())
        self.communities_cache = cache.get("communities", {})
        super().__init__(
            db_uri=db_uri,
            tmp_dir=tmp_dir,
            table_generators=[
                RDMRecordTableGenerator(
                    self.parents_cache,
                    self.records_cache,
                    self.communities_cache,
                ),
                RDMDraftTableGenerator(
                    self.parents_cache,
                    self.records_cache,
                    self.communities_cache,
                ),
                RDMVersionStateTableGenerator(self.parents_cache),
            ],
        )

    def _validate(self):
        """Validate data before loading."""
        pass
