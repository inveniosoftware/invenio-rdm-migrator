# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Transaction load errors."""


class TableNotFound(Exception):
    """Table not found for migration."""

    def __init__(self, table_name):
        """Constructor."""
        self.table_name = table_name

    @property
    def description(self):
        """Exception's description."""
        return (
            f"Cannot process transaction row. Table not configured: {self.table_name}"
        )
