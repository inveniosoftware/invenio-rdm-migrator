# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class PersistentIdentifier:
    """Persistent identifier dataclass model."""

    id: str
    pid_type: str
    pid_value: str
    status: str
    object_type: str
    object_uuid: str
    created: str
    updated: str

    _table_name: InitVar[str] = "pidstore_pid"
