# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from datetime import datetime

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.models import PersistentIdentifier
from ....load.postgresql import TableGenerator
from ..models import RDMDraftMetadata, RDMParentMetadata
from .parents import generate_parent_rows


class RDMDraftTableGenerator(TableGenerator):
    """RDM Record and related tables load."""

    def __init__(self, parent_cache, communities_cache):
        """Constructor."""
        super().__init__(
            tables=[
                RDMDraftMetadata,
                RDMParentMetadata,
                PersistentIdentifier,
            ],
            pks=[
                ("draft.id", generate_uuid),
                ("parent.id", generate_uuid),
                ("draft.json.pid", generate_recid),
                ("parent.json.pid", generate_recid),
                ("draft.parent_id", lambda d: d["parent"]["id"]),
            ],
        )
        self.parent_cache = parent_cache
        self.communities_cache = communities_cache

    def _generate_rows(self, data, **kwargs):
        """Generates rows for a record."""
        now = datetime.utcnow().isoformat()
        parent = data["parent"]
        draft = data.get("draft")
        if not draft:
            return

        record_pid = draft["json"]["pid"]
        rec_parent_id = self.parent_cache.get(parent["json"]["id"]).get("id")

        # FIXME: take into account draft position and add to next_draft_id
        if not self.parent_cache.get(parent["json"]["id"]):
            yield from generate_parent_rows(parent)

        yield RDMDraftMetadata(
            id=draft["id"],
            json=draft["json"],
            created=draft["created"],
            updated=draft["updated"],
            version_id=draft["version_id"],
            index=draft["index"],
            bucket_id=draft.get("bucket_id"),
            parent_id=rec_parent_id or draft["parent_id"],
            expires_at=draft["expires_at"],
            fork_version_id=draft["fork_version_id"],
        )
        # recid
        yield PersistentIdentifier(
            id=record_pid["pk"],
            pid_type=record_pid["pid_type"],  # FIXME: in rdm both are recid?
            pid_value=draft["json"]["id"],
            status=record_pid["status"],
            object_type=record_pid["obj_type"],
            object_uuid=draft["id"],
            created=now,
            updated=now,
        )
        # DOI
        if "doi" in draft["json"]["pids"]:
            yield PersistentIdentifier(
                id=pid_pk(),
                pid_type="doi",
                pid_value=draft["json"]["pids"]["doi"]["identifier"],
                status="R",
                object_type="rec",
                object_uuid=draft["id"],
                created=now,
                updated=now,
            )

    # FIXME: deduplicate with records.py
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

    def cleanup(self, db, **kwargs):
        """Cleanup."""
        pass
