# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record stream."""

from .load import RDMRecordCopyLoad
from .transform import RDMRecordEntry, RDMRecordTransform

__all__ = (
    "RDMRecordCopyLoad",
    "RDMRecordEntry",
    "RDMRecordTransform",
)
