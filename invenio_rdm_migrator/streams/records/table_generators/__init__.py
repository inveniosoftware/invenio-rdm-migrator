# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM records table generators."""

from .drafts import RDMDraftTableGenerator
from .records import RDMRecordTableGenerator
from .versions import RDMVersionStateTableGenerator

__all__ = (
    "RDMDraftTableGenerator",
    "RDMRecordTableGenerator",
    "RDMVersionStateTableGenerator",
)
