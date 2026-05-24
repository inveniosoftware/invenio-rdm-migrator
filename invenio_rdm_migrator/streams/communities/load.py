# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration users load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generator import CommunityTableGenerator


class CommunityCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL communities COPY load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[CommunityTableGenerator()], **kwargs)
