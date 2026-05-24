# SPDX-FileCopyrightText: 2022 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration record stream."""

from .transform import RDMRecordEntry, RDMRecordTransform

__all__ = (
    "RDMRecordEntry",
    "RDMRecordTransform",
)
