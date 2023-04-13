# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration users load module."""

from ...load import PostgreSQLCopyLoad
from .table_generator import UserTableGenerator


class UserCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL users COPY load."""

    def __init__(self, db_uri=None, tmp_dir=None, cache=None):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[
                UserTableGenerator(),
            ],
            tmp_dir=tmp_dir,
        )

    def _validate(self):
        """Validate data before loading."""
        return True
