# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identifiers generators module."""

import random
from uuid import uuid4


def generate_uuid(data):
    """Generate a UUID."""
    return str(uuid4())


# keep track of generated PKs, since there's a chance they collide
GENERATED_PID_PKS = set()


def pid_pk():
    """Generate a numeric primary key."""
    while True:
        # we start at 1M to avoid collisions with existing low-numbered PKs
        val = random.randint(1_000_000, 2_147_483_647 - 1)
        if val not in GENERATED_PID_PKS:
            GENERATED_PID_PKS.add(val)
            return val


def generate_recid(data):
    """Generate a record id object."""
    return {
        "pk": pid_pk(),
        "obj_type": "rec",
        "pid_type": "recid",
        "status": "R",
    }
