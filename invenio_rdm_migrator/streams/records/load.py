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
    """PostgreSQL COPY load."""

    def __init__(self, versioning=True, **kwargs):
        """Constructor."""
        table_generators = [RDMRecordTableGenerator(), RDMDraftTableGenerator()]

        if versioning:
            table_generators.append(RDMVersionStateTableGenerator())

        super().__init__(table_generators=table_generators, **kwargs)
