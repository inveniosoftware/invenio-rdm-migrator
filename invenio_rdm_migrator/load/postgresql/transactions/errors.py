# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Transaction load errors."""


class TableNotFound(Exception):
    """Table not found for migration."""

    def __init__(self, table_name):
        """Constructor."""
        super().__init__(
            f"Cannot process transaction row. Table not configured: {self.table_name}"
        )
