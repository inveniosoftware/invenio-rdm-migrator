# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Existing data table generator module."""

from .table import TableGenerator


class ExistingDataTableGenerator(TableGenerator):
    """Table generator to import data directly from existing data.

    This is useful when the data_dir already contain the files (e.g. csv) with
    the contents to be imported, for example from a previous migration run. Using
    this table generator the Extract and Transform steps can be skipped.
    """

    def __init__(self, tables, pks=None, post_load_hooks=None):
        """Constructor."""
        # forces pks to None since they won't be used
        super().__init__(
            tables, pks=None, post_load_hooks=post_load_hooks, existing_data=True
        )
