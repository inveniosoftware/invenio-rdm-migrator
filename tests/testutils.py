# SPDX-FileCopyrightText: 2023 CERN.
# SPDX-License-Identifier: MIT

"""Test utilities."""

import sqlalchemy as sa


def assert_model_count(session, model_cls, count):
    """Assert row count for a model."""
    assert session.scalar(sa.select(sa.func.count()).select_from(model_cls)) == count
