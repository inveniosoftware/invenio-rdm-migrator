# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Awards loader."""

from ...load.postgresql.bulk import PostgreSQLCopyLoad
from ...load.postgresql.bulk.generators import ExistingDataTableGenerator
from ..models.awards import Awards


class ExistingAwardsLoad(PostgreSQLCopyLoad):
    """Existing awards class for data loading."""

    def __init__(self, db_uri, data_dir, **kwargs):
        """Constructor."""
        super().__init__(
            db_uri=db_uri,
            table_generators=[ExistingDataTableGenerator(tables=[Awards], pks=[])],
            data_dir=data_dir,
            existing_data=True,
        )
