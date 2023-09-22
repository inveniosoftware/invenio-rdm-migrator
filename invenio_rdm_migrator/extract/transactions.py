# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transaction extract classes."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Tx:
    """An extracted DB transaction."""

    id: int
    operations: list[dict]  # TODO: we could more narrowly define it later
    commit_lsn: Optional[int] = None
