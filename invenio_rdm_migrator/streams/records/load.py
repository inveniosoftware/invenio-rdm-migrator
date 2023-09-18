# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generators import (
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
