# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Files actions module."""

from dataclasses import dataclass

from ....actions import LoadAction, LoadData
from ....load.ids import generate_uuid
from ....load.postgresql.transactions.operations import Operation, OperationType
from ....state import STATE
from ...models.files import FilesBucket, FilesInstance, FilesObjectVersion
from ...models.records import RDMDraftFile


@dataclass
class FileUploadData(LoadData):
    """File upload action data."""

    bucket: dict
    object_version: dict
    file_instance: dict
    file_record: dict


class FileUploadAction(LoadAction):
    """RDM draft creation."""

    name = "upload-file"
    data_cls = FileUploadData
    pks = [("file_record", "id", generate_uuid)]

    def _generate_rows(self, **kwargs):
        """Generates rows for a new draft."""
        # if we were to use the state for consistency checks
        # the bucket should already exist
        yield Operation(OperationType.UPDATE, FilesBucket, self.data.bucket)
        yield Operation(
            OperationType.INSERT, FilesObjectVersion, self.data.object_version
        )
        yield Operation(OperationType.INSERT, FilesInstance, self.data.file_instance)

        self.data.file_record["record_id"] = STATE.BUCKETS.get(
            self.data.file_record["id"]
        )
        yield Operation(OperationType.INSERT, RDMDraftFile, self.data.file_record)
