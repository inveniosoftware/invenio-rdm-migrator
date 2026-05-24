# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM records table generators."""

from .deleted_records import RDMDeletedRecordTableGenerator
from .drafts import RDMDraftTableGenerator
from .records import RDMRecordTableGenerator
from .versions import RDMVersionStateTableGenerator

__all__ = (
    "RDMDraftTableGenerator",
    "RDMRecordTableGenerator",
    "RDMVersionStateTableGenerator",
    "RDMDeletedRecordTableGenerator",
)
