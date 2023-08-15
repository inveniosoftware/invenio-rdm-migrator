# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration parent table load module."""

from datetime import datetime

from ....load.postgresql.transactions.operations import Operation, OperationType
from ...models.pids import PersistentIdentifier
from ...models.records import RDMParentMetadata


def generate_parent_ops(parent, parent_pid):
    """Generates operations for a parent record."""
    now = datetime.utcnow().isoformat()
    # order is important when doing action/streaming migration
    # parent recid
    yield Operation(
        OperationType.INSERT,
        PersistentIdentifier,
        dict(
            id=parent_pid["id"],
            pid_type=parent_pid["pid_type"],
            pid_value=parent_pid["pid_value"],
            status=parent_pid["status"],
            object_type=parent_pid["object_type"],
            object_uuid=parent["id"],
            created=now,
            updated=now,
        ),
    )
    # parent record
    yield Operation(
        OperationType.INSERT,
        RDMParentMetadata,
        dict(
            id=parent["id"],
            json=parent["json"],
            created=parent["created"],
            updated=parent["updated"],
            version_id=parent["version_id"],
        ),
    )
