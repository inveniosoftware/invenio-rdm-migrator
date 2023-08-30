# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration parent table load module."""

from datetime import datetime

from invenio_rdm_migrator.load.ids import pid_pk

from ...models.pids import PersistentIdentifier
from ...models.records import RDMParentMetadata


def generate_parent_rows(parent):
    """Generates rows for a parent record."""
    now = datetime.utcnow().isoformat()
    parent_pid = parent["json"]["pid"]
    # order is important when doing action/streaming migration
    # parent recid
    yield PersistentIdentifier(
        id=parent_pid["pk"],
        pid_type=parent_pid["pid_type"],
        pid_value=parent["json"]["id"],
        status=parent_pid["status"],
        object_type=parent_pid["obj_type"],
        object_uuid=parent["id"],
        created=now,
        updated=now,
    )
    # parent DOI
    parent_doi = parent["json"].get("pids", {}).get("doi")
    if parent_doi and parent_doi["identifier"]:
        yield PersistentIdentifier(
            id=pid_pk(),
            pid_type="doi",
            pid_value=parent_doi["identifier"],
            status="R",
            object_type="rec",
            object_uuid=parent["id"],
            created=now,
            updated=now,
        )

    # parent record
    yield RDMParentMetadata(
        id=parent["id"],
        json=parent["json"],
        created=parent["created"],
        updated=parent["updated"],
        version_id=parent["version_id"],
    )
