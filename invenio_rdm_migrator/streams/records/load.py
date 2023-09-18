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
        table_generators = [RDMRecordTableGenerator()]
        super().__init__(table_generators=table_generators, **kwargs)


class RDMDraftCopyLoad(PostgreSQLCopyLoad):
    """RDM draft copy load."""

    def __init__(self, **kwargs):
        """Constructor."""
        table_generators = [RDMDraftTableGenerator(), RDMVersionStateTableGenerator()]
        super().__init__(table_generators=table_generators, **kwargs)
