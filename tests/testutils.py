# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Test utilities."""

import sqlalchemy as sa


def assert_model_count(session, model_cls, count):
    """Assert row count for a model."""
    assert session.scalar(sa.select(sa.func.count()).select_from(model_cls)) == count
