# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""File actions tests."""

from datetime import datetime
from uuid import uuid4

import pytest
import sqlalchemy as sa
from testutils import assert_model_count

from invenio_rdm_migrator.load.postgresql.transactions.operations import OperationType
from invenio_rdm_migrator.streams.actions.load import FileUploadAction
from invenio_rdm_migrator.streams.models.files import (
    FilesBucket,
    FilesInstance,
    FilesObjectVersion,
)
from invenio_rdm_migrator.streams.models.records import (
    RDMDraftFile,
    RDMDraftMediaFile,
    RDMDraftMetadata,
)


@pytest.fixture(scope="function")
def draft(
    session,
    database,
    bucket_data_w_size,
):
    """Draft with bucket."""
    session.add(FilesBucket(**bucket_data_w_size))
    session.add(
        RDMDraftMetadata(
            id="5cbdc04b-b2ab-4d25-b21c-3ce6a5269710",
            json={},
            created=datetime.utcnow(),
            updated=datetime.utcnow(),
            version_id=1,
            index=1,
            bucket_id=bucket_data_w_size["id"],
            parent_id=uuid4(),
            expires_at=None,
            fork_version_id=None,
            media_bucket_id=None,
        )
    )
    session.commit()


@pytest.fixture(scope="function")
def draft_with_file(session, draft, fi_data, ov_data, fr_data):
    """Draft with one file."""
    session.add(FilesInstance(**fi_data))
    session.add(FilesObjectVersion(**ov_data))
    fr_data["id"] = uuid4()
    fr_data["record_id"] = "5cbdc04b-b2ab-4d25-b21c-3ce6a5269710"
    session.add(RDMDraftFile(**fr_data))
    session.commit()


def test_upload_file(
    session,
    database,
    pg_tx,
    draft,
    bucket_data_w_size,
    fi_data,
    ov_data,
    fr_data,
):
    """Test draft file upload replacement."""
    data = dict(
        bucket=bucket_data_w_size,
        object_version=ov_data,
        file_instance=fi_data,
        file_record=fr_data,
    )
    action = FileUploadAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 4
    bucket, fi, ov, draft_file = rows
    assert bucket.type == OperationType.UPDATE
    assert bucket.model == FilesBucket
    assert fi.type == OperationType.INSERT
    assert fi.model == FilesInstance
    assert ov.type == OperationType.INSERT
    assert ov.model == FilesObjectVersion
    assert draft_file.type == OperationType.INSERT
    assert draft_file.model == RDMDraftFile
    # still type str since it has not been inserted in DB
    assert str(draft_file.data["record_id"]) == "5cbdc04b-b2ab-4d25-b21c-3ce6a5269710"
    assert str(draft_file.data["object_version_id"]) == ov_data["version_id"]

    pg_tx.run([action])
    assert_model_count(session, FilesBucket, 1)
    assert_model_count(session, FilesObjectVersion, 1)
    assert_model_count(session, FilesInstance, 1)
    assert_model_count(session, RDMDraftFile, 1)


def test_upload_file_replacement(
    session,
    database,
    pg_tx,
    draft_with_file,
    bucket_data_w_size,
    fi_data,
    ov_data,
    fr_data,
):
    """Test draft file upload replacement."""
    fi_data["id"] = str(uuid4())
    ov_data["file_id"] = fi_data["id"]
    ov_data["version_id"] = str(uuid4())
    data = dict(
        bucket=bucket_data_w_size,
        object_version=ov_data,
        file_instance=fi_data,
        file_record=fr_data,
    )
    action = FileUploadAction(data)
    rows = list(action.prepare(session))

    assert len(rows) == 5
    bucket, old_ov, fi, new_ov, draft_file = rows
    assert bucket.type == OperationType.UPDATE
    assert bucket.model == FilesBucket
    assert old_ov.type == OperationType.UPDATE
    assert old_ov.model == FilesObjectVersion
    assert str(old_ov.data["version_id"]) == "f8200dc7-55b6-4785-abd0-f3d13b143c98"
    assert fi.type == OperationType.INSERT
    assert fi.model == FilesInstance
    assert new_ov.type == OperationType.INSERT
    assert new_ov.model == FilesObjectVersion
    assert draft_file.type == OperationType.UPDATE
    assert draft_file.model == RDMDraftFile
    assert str(draft_file.data["record_id"]) == "5cbdc04b-b2ab-4d25-b21c-3ce6a5269710"
    assert str(draft_file.data["object_version_id"]) == ov_data["version_id"]

    pg_tx.run([action])
    assert_model_count(session, FilesBucket, 1)
    assert_model_count(session, FilesObjectVersion, 2)
    assert_model_count(session, FilesInstance, 2)
    assert_model_count(session, RDMDraftFile, 1)
