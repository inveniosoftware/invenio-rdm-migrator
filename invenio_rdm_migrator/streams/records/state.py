# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Records state module."""

from ...state import StateValidator


class ParentModelValidator(StateValidator):
    """Parent state entry validator."""

    @classmethod
    def validate(cls, data):
        """Data validation."""
        latest_id = data.get("latest_id")
        assert latest_id or data.get("next_draft_id")
        if latest_id:
            assert data.get("latest_index")
