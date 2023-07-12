# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Persistent identifier table generators."""

from ...load.ids import generate_pk
from ...load.postgresql.transactions.generators import SingleRowGenerator
from ...load.postgresql.transactions.operations import Operation
from ..models.pids import PersistentIdentifier


class PIDRowGenerator(SingleRowGenerator):
    """Persistent identifier table generator."""

    def __init__(self, pids_state, **kwargs):
        """Constructor."""
        super().__init__(
            table=PersistentIdentifier, pks=[("id", generate_pk)], **kwargs
        )
        self.pids_state = pids_state

    # FIXME: not generic enough
    # all memory tg enforce op, in the long run this is not re-usable
    def _generate_rows(self, data, op, **kwargs):
        """Yield generated rows."""
        if data["pid_type"] != "depid":
            # FIXME: temporary fix to test the microseconds conversion
            # should be moved to a mixin or similar on the transform step
            from datetime import datetime

            data["created"] = datetime.fromtimestamp(data["created"] / 1_000_000)
            data["updated"] = datetime.fromtimestamp(data["updated"] / 1_000_000)

            self.pids_state.add(
                data["pid_value"],  # recid
                {
                    "id": data["id"],
                    "pid_type": data["pid_type"],
                    "status": data["status"],
                    "obj_type": data["object_type"],
                    "created": data["created"],
                },
            )
            yield Operation(op, self.table(**data))
