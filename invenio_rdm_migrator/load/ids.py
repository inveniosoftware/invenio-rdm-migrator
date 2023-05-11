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


def initialize_pid_pk_value(value):
    """Set the value for the initial pid_pk emitted."""
    pid_pk.value = value


def pid_pk():
    """Generate an autoincrementing numeric primary key."""
    if not hasattr(pid_pk, "value"):
        pid_pk.value = 1_000_000
    else:
        pid_pk.value += 1
    return pid_pk.value


def generate_recid(data, status="R"):
    """Generate a record id object."""
    return {
        "pk": pid_pk(),  # not the pid_value, that comes from rec.json.id in the tg
        "obj_type": "rec",
        "pid_type": "recid",
        "status": status,
    }
