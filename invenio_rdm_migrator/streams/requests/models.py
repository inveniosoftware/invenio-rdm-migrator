# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Dataclasses models to generate table rows."""

from dataclasses import InitVar, dataclass


@dataclass
class RequestMetadata:
    """RDM Record File dataclass model."""

    id: str
    json: dict
    created: str
    updated: str
    version_id: int
    number: str
    expires_at: str

    _table_name: InitVar[str] = "request_metadata"
