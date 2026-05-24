# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration record load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generators import (
    RDMDeletedRecordTableGenerator,
    RDMDraftTableGenerator,
    RDMRecordTableGenerator,
    RDMVersionStateTableGenerator,
)


class RDMRecordCopyLoad(PostgreSQLCopyLoad):
    """RDM record copy load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[RDMRecordTableGenerator()], **kwargs)


class RDMDraftCopyLoad(PostgreSQLCopyLoad):
    """RDM draft copy load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[RDMDraftTableGenerator()], **kwargs)


class RDMVersionStateCopyLoad(PostgreSQLCopyLoad):
    """RDM Vesion state copy load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[RDMVersionStateTableGenerator()], **kwargs)


class RDMDeletedRecordCopyLoad(PostgreSQLCopyLoad):
    """RDM deleted record copy load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[RDMDeletedRecordTableGenerator()], **kwargs)
