# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Invenio RDM migration PostgreSQL models module."""

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Model(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses."""

    type_annotation_map = {
        dict: JSONB,
    }
