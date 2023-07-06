# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration files table load module."""

from ...load.postgresql.bulk.generators import TableGenerator
from ..models.files import FilesBucket, FilesInstance, FilesObjectVersion


class FilesTableGenerator(TableGenerator):
    """Files and related tables load via CSV."""

    def __init__(self):
        """Constructor."""
        super().__init__(
            tables=[
                FilesInstance,
                FilesBucket,
                FilesObjectVersion,
            ],
        )

    def _generate_rows(self, data, **kwargs):
        bucket = data["bucket"]
        object_version = data["object_version"]
        file = data["file"]
        yield FilesInstance(**file)
        yield FilesBucket(**bucket)
        yield FilesObjectVersion(**object_version)
