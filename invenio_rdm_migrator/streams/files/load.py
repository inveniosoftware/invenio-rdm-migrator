# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration files load module."""

from ...load import PostgreSQLCopyLoad
from .table_generator import FilesTableGenerator


class FilesCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL files COPY load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(
            table_generators=[
                FilesTableGenerator(),
            ],
            **kwargs,
        )

    def _validate(self):
        """Validate data before loading."""
        return True
