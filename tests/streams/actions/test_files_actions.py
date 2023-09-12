# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File actions tests."""

from uuid import UUID

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import DraftFileUploadAction
from invenio_rdm_migrator.streams.models.files import (
    FilesBucket,
    FilesInstance,
    FilesObjectVersion,
)
from invenio_rdm_migrator.streams.models.records import RDMDraftFile


def test_upload_file_action(
    buckets_state, bucket_data_w_size, fi_data, ov_data, fr_data
):
    data = dict(
        tx_id=1,
        bucket=bucket_data_w_size,
        object_version=ov_data,
        file_instance=fi_data,
        file_record=fr_data,
    )
    action = DraftFileUploadAction(data)
    rows = list(action.prepare())

    assert len(rows) == 4
    assert rows[0].type == OperationType.UPDATE
    assert rows[0].model == FilesBucket
    assert rows[1].type == OperationType.INSERT
    assert rows[1].model == FilesObjectVersion
    assert rows[2].type == OperationType.INSERT
    assert rows[2].model == FilesInstance
    assert rows[3].type == OperationType.INSERT
    assert rows[3].model == RDMDraftFile
    UUID(rows[3].data["id"])  # would raise value error if not UUID or None
    # still type str since it has not been inserted in DB
    assert rows[3].data["record_id"] == "d94f793c-47d2-48e2-9867-ca597b4ebb41"
