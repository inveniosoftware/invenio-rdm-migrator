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

    def __init__(self, state, versioning=True, **kwargs):
        """Constructor."""
        self.parents_state = state["parents"]
        self.records_state = state["records"]
        self.communities_state = state["communities"]
        table_generators = [
            RDMRecordTableGenerator(
                self.parents_state,
                self.records_state,
                self.communities_state,
            ),
            RDMDraftTableGenerator(
                self.parents_state,
                self.records_state,
                self.communities_state,
            ),
        ]

        if versioning:
            table_generators.append(RDMVersionStateTableGenerator(self.parents_state))

        super().__init__(table_generators=table_generators, **kwargs)
