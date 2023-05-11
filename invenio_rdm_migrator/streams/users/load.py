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

    def __init__(self, db_uri, data_dir, **kwargs):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            data_dir=data_dir,
            table_generators=[
                UserTableGenerator(),
            ],
            **kwargs,
        )

    def _validate(self):
        """Validate data before loading."""
        return True
