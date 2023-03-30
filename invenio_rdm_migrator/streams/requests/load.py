# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration requests load module."""

from ...load import PostgreSQLCopyLoad
from .table_generator import RequestTableGenerator


class RequestCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL COPY load."""

    def __init__(self, cache, db_uri, tmp_dir):
        """Constructor."""
        self.communities_cache = cache.get("communities", {})
        super().__init__(
            db_uri=db_uri,
            tmp_dir=tmp_dir,
            table_loads=[
                RequestTableGenerator(self.communities_cache),
            ],
        )

    def _validate(self):
        """Validate data before loading."""
        pass
