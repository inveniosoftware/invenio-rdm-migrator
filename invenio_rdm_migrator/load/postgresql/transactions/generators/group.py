# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Transaction group generator module."""

from .....logging import Logger
from ..errors import TableNotFound


class TxGenerator:
    """Maps a table name to a table generator."""

    def __init__(self, table_to_generator_map):
        """Constructor."""
        self.mapping = table_to_generator_map

    # accepting naming suggestions for this method
    def prepare(self, table_name, op, data):
        """Returns the corresponding rows for a row data."""
        tgs = self.mapping.get(table_name, None)
        if not tgs:
            logger = Logger.get_logger()
            logger.exception(f"Could not find table generator for table {table_name}")
            raise TableNotFound(table_name)

        entries = []
        if isinstance(tgs, list):
            for tg in tgs:
                entries.extend(list(tg.prepare(data, op=op)))
        else:
            entries.extend(list(tgs.prepare(data, op=op)))

        return entries
