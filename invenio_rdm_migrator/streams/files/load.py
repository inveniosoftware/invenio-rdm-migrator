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

    def __init__(self, db_uri=None, tmp_dir=None, cache=None):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[
                FilesTableGenerator(),
            ],
            tmp_dir=tmp_dir,
        )

    def _validate(self):
        """Validate data before loading."""
        return True
