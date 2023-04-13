# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from datetime import datetime

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.models import PersistentIdentifier
from ....load.postgresql import TableGenerator
from ...communities.models import RDMParentCommunityMetadata
from ..models import RDMParentMetadata, RDMRecordFile, RDMRecordMetadata
from .parents import generate_parent_rows


def generate_files_uuids(data):
    """Generate uuid for every file in the list.

    Return the transformed list with the generated ids.
    """
    _files = data["record_files"]
    for _file in _files:
        _file["id"] = generate_uuid({})
    return _files


def generate_record_uuid(data):
    """Generate record uuid if not present."""
    _id = data.get("id")
    return _id if _id else generate_uuid(None)


class RDMRecordTableGenerator(TableGenerator):
    """RDM Record and related tables load."""

    def __init__(self, parent_cache, communities_cache):
        """Constructor."""
        super().__init__(
            tables=[
                PersistentIdentifier,
                RDMParentMetadata,
                RDMRecordMetadata,
                RDMParentCommunityMetadata,
                RDMRecordFile,
            ],
            pks=[
                ("record.id", generate_record_uuid),
                ("parent.id", generate_uuid),
                ("record.json.pid", generate_recid),
                ("parent.json.pid", generate_recid),
                ("record.parent_id", lambda d: d["parent"]["id"]),
                ("record_files", generate_files_uuids),
            ],
        )
        self.parent_cache = parent_cache
        self.communities_cache = communities_cache

    def _generate_rows(self, data, **kwargs):
        """Generates rows for a record."""
        now = datetime.utcnow().isoformat()
        parent = data["parent"]
        record = data.get("record")
        if not record:
            return

        record_pid = record["json"]["pid"]
        # parent
        if not self.parent_cache.get(parent["json"]["id"]):
            self.parent_cache.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "latest_index": record["index"],
                    "latest_id": record["id"],
                },
            )
            yield from generate_parent_rows(parent)
            # parent community
            if "default" in parent["json"]["communities"]:
                yield RDMParentCommunityMetadata(
                    community_id=parent["json"]["communities"]["default"],
                    record_id=parent["id"],
                    request_id=None,
                )
        else:
            # parent in cache - update version
            cached_parent = self.parent_cache[parent["json"]["id"]]
            # check if current record is a new version of the cached one
            if cached_parent["latest_index"] < record["index"]:
                cached_parent["latest_index"] = record["index"]
                cached_parent["latest_id"] = record["id"]
                # if there is a larger version the draft is old
                cached_parent["next_draft_id"] = None

        # record
        yield RDMRecordMetadata(
            id=record["id"],
            json=record["json"],
            created=record["created"],
            updated=record["updated"],
            version_id=record["version_id"],
            index=record["index"],
            bucket_id=record.get("bucket_id"),
            parent_id=record["parent_id"],
        )
        # recid
        yield PersistentIdentifier(
            id=record_pid["pk"],
            pid_type=record_pid["pid_type"],
            pid_value=record["json"]["id"],
            status=record_pid["status"],
            object_type=record_pid["obj_type"],
            object_uuid=record["id"],
            created=now,
            updated=now,
        )
        # DOI
        if "doi" in record["json"]["pids"]:
            yield PersistentIdentifier(
                id=pid_pk(),
                pid_type="doi",
                pid_value=record["json"]["pids"]["doi"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=record["id"],
                created=now,
                updated=now,
            )
        # OAI
        if "oai" in record["json"]["pids"]:
            yield PersistentIdentifier(
                id=pid_pk(),
                pid_type="oai",
                pid_value=record["json"]["pids"]["oai"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=record["id"],
                created=now,
                updated=now,
            )

        # record files
        record_files = data["record_files"]
        for _file in record_files:
            yield RDMRecordFile(
                id=_file["id"],
                json=_file["json"],
                created=_file["created"],
                updated=_file["updated"],
                version_id=_file["version_id"],
                key=_file["key"],
                record_id=record["id"],
                object_version_id=_file["object_version_id"],
            )

    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""

        def _resolve_communities(communities):
            default_slug = communities.get("default")
            default_id = self.communities_cache.get(default_slug)
            if not default_id:
                # TODO: maybe raise error without correct default community?
                communities = {}
            communities["default"] = default_id

            communities_slugs = communities.get("ids", [])
            _ids = []
            for slug in communities_slugs:
                _id = self.communities_cache.get(slug)
                if _id:
                    _ids.append(_id)
            communities["ids"] = _ids

        # resolve parent communities slug
        parent = data["parent"]
        communities = parent["json"].get("communities")
        if communities:
            _resolve_communities(communities)

    def _cleanup_db(self):
        """Cleanup DB after load."""
        # FIXME: abstract to tables, can we do without invenio imports
        # cant fix atm, versions state needs to be deleted in the middle
        # from invenio_db import db
        # from invenio_pidstore.models import PersistentIdentifier
        # from invenio_rdm_records.records.models import (
        #     RDMDraftMetadata,
        #     RDMParentMetadata,
        #     RDMRecordMetadata,
        #     RDMVersionsState,
        # )
        # PersistentIdentifier.query.filter(
        #     PersistentIdentifier.pid_type.in_(("recid", "doi", "oai")),
        #     PersistentIdentifier.object_type == "rec",
        # ).delete()
        # RDMVersionsState.query.delete()
        # RDMRecordMetadata.query.delete()
        # RDMParentMetadata.query.delete()
        # RDMDraftMetadata.query.delete()
        # db.session.commit()
        pass

    def _cleanup_files(self):
        """Cleanup files after load."""
        # FIXME: tables does not return the name correct
        # delegate to table_generators?
        # for table in self.tables:
        #     fpath = self.tmp_dir / f"{table._table_name}.csv"
        #     print(f"Checking {fpath}")
        #     if fpath.exists():
        #         print(f"Deleting {fpath}")
        #         fpath.unlink(missing_ok=True)
        pass

    def cleanup(self, db, **kwargs):
        """Cleanup."""
        self._cleanup_files()

        if db:  # DB cleanup is not always desired
            self._cleanup_db()
