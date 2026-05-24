# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Names loader."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from ...load.postgresql.bulk.generators import ExistingDataTableGenerator
from ..models.names import Name


class ExistingNamesLoad(PostgreSQLCopyLoad):
    """Existing names class for data loading."""

    def __init__(self, db_uri, data_dir, **kwargs):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[ExistingDataTableGenerator(tables=[Name], pks=[])],
            data_dir=data_dir,
            existing_data=True,
        )
