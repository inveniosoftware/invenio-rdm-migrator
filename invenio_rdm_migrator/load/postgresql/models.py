# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration PostgreSQL models module."""

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Model(MappedAsDataclass, DeclarativeBase):
    """subclasses will be converted to dataclasses."""

    type_annotation_map = {
        dict: JSONB,
    }
