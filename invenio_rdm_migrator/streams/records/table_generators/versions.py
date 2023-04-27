# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from ....load.postgresql import TableGenerator
from ..models import RDMVersionState


class RDMVersionStateTableGenerator(TableGenerator):
    """RDM version state computed table."""

    def __init__(self, parents_cache):
        """Constructor."""
        super().__init__(tables=[RDMVersionState])
        self.parents_cache = parents_cache

    def _generate_rows(self, parent_entry, **kwargs):
        # Version state to be populated in the end from the final state
        yield RDMVersionState(
            latest_index=parent_entry["latest_index"],
            parent_id=parent_entry["id"],
            latest_id=parent_entry["latest_id"],
            next_draft_id=parent_entry["next_draft_id"],
        )

    def prepare(self, tmp_dir, entry, stack, output_files, **kwargs):
        """Compute rows."""
        # overwrite to avoid it using the parent class on a per
        pass

    def post_prepare(self, tmp_dir, stack, output_files, **kwargs):
        """Overwrite entries with parent cache entries."""
        for entry in self.parents_cache.all():
            super().prepare(tmp_dir, entry, stack, output_files, **kwargs)
