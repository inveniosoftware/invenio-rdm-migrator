# SPDX-FileCopyrightText: 2022-2023 CERN.
# SPDX-License-Identifier: MIT

"""Funders loader."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from ...load.postgresql.bulk.generators import ExistingDataTableGenerator
from ..models.funders import Funders


class ExistingFundersLoad(PostgreSQLCopyLoad):
    """Existing funders class for data loading."""

    def __init__(self, db_uri, data_dir, **kwargs):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[ExistingDataTableGenerator(tables=[Funders], pks=[])],
            data_dir=data_dir,
            existing_data=True,
        )
