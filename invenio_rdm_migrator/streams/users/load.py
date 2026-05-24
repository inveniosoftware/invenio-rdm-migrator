# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration users load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generator import UserTableGenerator


class UserCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL users COPY load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                UserTableGenerator(),
            ],
            **kwargs,
        )
