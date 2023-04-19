# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.
"""Invenio RDM migration featured communities load module."""

from ...load import PostgreSQLCopyLoad
from .table_generator import FeaturedCommunityTableGenerator


class FeaturedCommunityCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL communities COPY load."""

    def __init__(self, cache, db_uri=None, tmp_dir=None):
        """Constructor."""
        self.communities_cache = cache.get("communities", {})
        super().__init__(
            db_uri=db_uri,
            table_loads=[
                FeaturedCommunityTableGenerator(
                    communities_cache=self.communities_cache
                ),
            ],
            tmp_dir=tmp_dir,
        )

    def _validate(self):
        """Validate data before loading."""
        return True
