# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration files table load module."""

from functools import partial

from ...load.postgresql.transactions.generators import SingleRowGenerator
from ..models.files import FilesBucket  # FIXME: should move all models to the root?

FilesBucketRowGenerator = partial(SingleRowGenerator, table=FilesBucket)
"""Memory only, no csv."""
