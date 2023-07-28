# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration requests load module."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from .table_generator import RequestTableGenerator


class RequestCopyLoad(PostgreSQLCopyLoad):
    """PostgreSQL COPY load."""

    def __init__(self, **kwargs):
        """Constructor."""
        super().__init__(table_generators=[RequestTableGenerator()], **kwargs)
