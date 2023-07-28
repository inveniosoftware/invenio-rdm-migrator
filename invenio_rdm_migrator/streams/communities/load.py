# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration users load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generator import CommunityTableGenerator


class CommunityCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL communities COPY load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[CommunityTableGenerator()], **kwargs)
