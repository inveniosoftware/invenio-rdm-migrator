# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from uuid import UUID

from ....load.postgresql.bulk.generators import TableGenerator
from ....state import STATE
from ...models.communities import RDMParentCommunityMetadata
from ...models.records import RDMVersionState


def _is_valid_uuid(value):
    try:
        UUID(value)
        return True
    except Exception:
        return False


class RDMVersionStateTableGenerator(TableGenerator):
    """RDM version state computed table."""

    def __init__(self):
        """Constructor."""
        super().__init__(tables=[RDMVersionState, RDMParentCommunityMetadata])

    def _generate_rows(self, parent_entry, **kwargs):
        # Version state to be populated in the end from the final state
        yield RDMVersionState(
            latest_index=parent_entry.get("latest_index"),
            parent_id=parent_entry["id"],
            latest_id=parent_entry.get("latest_id"),
            next_draft_id=parent_entry.get("next_draft_id"),
        )
        # Generate parent community rows
        communities = parent_entry.get("communities", [])
        for comm_id in communities:
            if _is_valid_uuid(comm_id):
                yield RDMParentCommunityMetadata(
                    record_id=parent_entry["id"],
                    community_id=comm_id,
                )

    def prepare(self, tmp_dir, entry, stack, output_files, **kwargs):
        """Compute rows."""
        # overwrite to avoid it using the parent class
        pass

    def post_prepare(self, tmp_dir, stack, output_files, **kwargs):
        """Overwrite entries with parent state entries."""
        for entry in STATE.PARENTS.all():
            super().prepare(tmp_dir, entry, stack, output_files, **kwargs)
