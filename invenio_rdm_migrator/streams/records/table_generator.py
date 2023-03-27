# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""


import random
from datetime import datetime

from ...load.models import PersistentIdentifier
from ...load.postgresql import TableGenerator, generate_uuid
from ..communities.models import RDMParentCommunityMetadata
from .models import RDMParentMetadata, RDMRecordMetadata, RDMVersionState


class RDMVersionStateTableGenerator(TableGenerator):
    """RDM version state computed table."""

    def __init__(self, parent_cache):
        """Constructor."""
        super().__init__(tables=[RDMVersionState])
        self.parent_cache = parent_cache

    def _generate_rows(self, parent_entry, **kwargs):
        # Version state to be populated in the end from the final state
        yield RDMVersionState(
            latest_index=parent_entry["version"]["latest_index"],
            parent_id=parent_entry["id"],
            latest_id=parent_entry["version"]["latest_id"],
            next_draft_id=None,
        )

    def prepare(self, tmp_dir, entries, **kwargs):
        """Overwrite entries with parent cache entries."""
        return super().prepare(tmp_dir, self.parent_cache.values(), **kwargs)

    def cleanup(self, **kwargs):
        """Cleanup."""
        pass


# keep track of generated PKs, since there's a chance they collide
GENERATED_PID_PKS = set()


def _pid_pk():
    while True:
        # we start at 1M to avoid collisions with existing low-numbered PKs
        val = random.randint(1_000_000, 2_147_483_647 - 1)
        if val not in GENERATED_PID_PKS:
            GENERATED_PID_PKS.add(val)
            return val


def _generate_recid(data):
    return {
        "pk": _pid_pk(),
        "obj_type": "rec",
        "pid_type": "recid",
        "status": "R",
    }


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
            ],
            pks=[
                ("record.id", generate_uuid),
                ("parent.id", generate_uuid),
                ("record.json.pid", _generate_recid),
                ("parent.json.pid", _generate_recid),
                ("record.parent_id", lambda d: d["parent"]["id"]),
            ],
        )
        self.parent_cache = parent_cache
        self.communities_cache = communities_cache

    def _generate_rows(self, data, **kwargs):
        now = datetime.utcnow().isoformat()

        # record
        rec = data["record"]
        record_pid = rec["json"]["pid"]
        parent = data["parent"]
        rec_parent_id = self.parent_cache.get(parent["json"]["id"], {}).get("id")
        yield RDMRecordMetadata(
            id=rec["id"],
            json=rec["json"],
            created=rec["created"],
            updated=rec["updated"],
            version_id=rec["version_id"],
            index=rec["index"],
            bucket_id=rec.get("bucket_id"),
            parent_id=rec_parent_id or rec["parent_id"],
        )
        # recid
        yield PersistentIdentifier(
            id=record_pid["pk"],
            pid_type=record_pid["pid_type"],
            pid_value=rec["json"]["id"],
            status=record_pid["status"],
            object_type=record_pid["obj_type"],
            object_uuid=rec["id"],
            created=now,
            updated=now,
        )
        # DOI
        if "doi" in rec["json"]["pids"]:
            yield PersistentIdentifier(
                id=_pid_pk(),
                pid_type="doi",
                pid_value=rec["json"]["pids"]["doi"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=rec["id"],
                created=now,
                updated=now,
            )
        # OAI
        if "oai" in rec["json"]["pids"]:
            yield PersistentIdentifier(
                id=_pid_pk(),
                pid_type="oai",
                pid_value=rec["json"]["pids"]["oai"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=rec["id"],
                created=now,
                updated=now,
            )

        # parent
        if parent["json"]["id"] not in self.parent_cache:
            self.parent_cache[parent["json"]["id"]] = dict(
                id=parent["id"],
                version=dict(latest_index=rec["index"], latest_id=rec["id"]),
            )
            parent_pid = parent["json"]["pid"]
            # record
            yield RDMParentMetadata(
                id=parent["id"],
                json=parent["json"],
                created=parent["created"],
                updated=parent["updated"],
                version_id=parent["version_id"],
            )
            # recid
            yield PersistentIdentifier(
                id=parent_pid["pk"],
                pid_type=parent_pid["pid_type"],
                pid_value=parent["json"]["id"],
                status=parent_pid["status"],
                object_type=parent_pid["obj_type"],
                object_uuid=parent["id"],
                created=now,
                updated=now,
            )
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
            if cached_parent["version"]["latest_index"] < rec["index"]:
                cached_parent["version"] = dict(
                    latest_index=rec["index"], latest_id=rec["id"]
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
        # delegate to table_loads?
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
