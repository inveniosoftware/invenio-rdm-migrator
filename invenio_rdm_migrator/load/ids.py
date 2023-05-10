# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identifiers generators module."""

from uuid import uuid4


def generate_uuid(data):
    """Generate a UUID."""
    return str(uuid4())


def pid_pk(initial_pid=1_000_000):
    """Generate an autoincrementing numeric primary key."""
    if not hasattr(pid_pk, "value"):
        pid_pk.value = initial_pid
    else:
        pid_pk.value += 1
    return pid_pk.value


def generate_recid(data, status="R", initial_pid=1_000_000):
    """Generate a record id object."""
    return {
        "pk": pid_pk(
            initial_pid
        ),  # not the pid_value, that comes from rec.json.id in the tg
        "obj_type": "rec",
        "pid_type": "recid",
        "status": status,
    }
