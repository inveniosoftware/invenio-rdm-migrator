# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Statement module."""

from enum import Enum


class Statement(Enum):
    """Represents the possible SQL operations supported by the migrator."""

    INSERT = "I"
    UPDATE = "U"
    DELETE = "D"
