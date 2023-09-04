# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration requests table load module."""


from ...load.ids import generate_uuid
from ...load.postgresql.bulk.generators import TableGenerator
from ...state import STATE
from ..models.requests import RequestMetadata


class RequestTableGenerator(TableGenerator):
    """Requests and related tables load."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[RequestMetadata],
            pks=[("id", generate_uuid)],
        )

    def _generate_rows(self, data, **kwargs):
        """Yield requests metadata."""
        request = data
        yield RequestMetadata(
            id=request["id"],
            json=request["json"],
            created=request["created"],
            updated=request["updated"],
            version_id=request["version_id"],
            number=request["number"],
            expires_at=request["expires_at"],
        )

    def _resolve_references(self, data, **kwargs):
        """Resolve references.

        Translates community slugs to uuids, and record parent pids to uuids. Both values
        are mandatory, therefore they are access as dict.

        :raises: KeyError if the the parent or community are not found in the state.
        """
        # it assumes the data is transformed by an InclusionRequestEntry
        request_slug = data["json"]["receiver"]["community"]
        community = STATE.COMMUNITIES.get(request_slug)

        data["json"]["receiver"]["community"] = community["id"]

    def prepare(self, tmp_dir, entry, stack, output_files, **kwargs):
        """Compute rows."""
        super().prepare(tmp_dir, entry, stack, output_files, create=True, **kwargs)
