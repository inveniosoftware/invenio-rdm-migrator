# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identifiers generators module."""

from uuid import uuid4

from ..state import STATE


def generate_uuid(data):
    """Generate a UUID."""
    return str(uuid4())


def pid_pk():
    """Generate an autoincrementing numeric primary key."""
    state = STATE.VALUES
    state_value = state.get("max_pid_pk")
    if not state_value:
        value = 1_000_000
        state.add("max_pid_pk", {"value": 1_000_000})
    else:
        value = state_value["value"] + 1
        state.update("max_pid_pk", {"value": value})

    return value


def generate_pk(data):
    """Generate a primery key."""
    return pid_pk()


def generate_recid(data, status="R"):
    """Generate a record id object."""
    # pk is not the pid_value, that comes from rec.json.id in the tg
    return {
        "pk": pid_pk(),
        # keep obj_type since the record needs this key dereferenced
        "obj_type": "rec",
        "pid_type": "recid",
        "status": status,
    }
