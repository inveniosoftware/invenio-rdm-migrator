# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration users load module."""

from ...load import PostgreSQLCopyLoad
from .table_generator import CommunityTableGenerator


class CommunityCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL communities COPY load."""

    def __init__(self, cache, db_uri=None, tmp_dir=None):
        """Constructor."""
        self.communities_cache = cache.get("communities", {})
        super().__init__(
            db_uri=db_uri,
            table_generators=[
                CommunityTableGenerator(communities_cache=self.communities_cache),
            ],
            tmp_dir=tmp_dir,
        )

    def _validate(self):
        """Validate data before loading."""
        return True
