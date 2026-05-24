# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration requests load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generator import RequestTableGenerator


class RequestCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL COPY load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[RequestTableGenerator()], **kwargs)
