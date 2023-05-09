# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from datetime import datetime
from functools import partial

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.models import PersistentIdentifier
from ....load.postgresql import TableGenerator
from ..models import RDMDraftMetadata, RDMParentMetadata
from .parents import generate_parent_rows


class RDMDraftTableGenerator(TableGenerator):
    """RDM Record and related tables load."""

    def __init__(self, parents_cache, records_cache, communities_cache):
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
                ("draft.json.pid", partial(generate_recid, status="N")),
                ("parent.json.pid", generate_recid),
                ("draft.parent_id", lambda d: d["parent"]["id"]),
            ],
        )
        self.parents_cache = parents_cache
        self.records_cache = records_cache
        self.communities_cache = communities_cache

    def _generate_rows(self, data, **kwargs):
        """Generates rows for a record."""
        now = datetime.utcnow().isoformat()
        parent = data["parent"]
        draft = data.get("draft")
        if not draft:
            return

        # some legacy records have different pid value in deposit than record
        # however _deposit.pid.value would contain the correct one
        # if it is not legacy we get it from the current field (json.id)
        recid = draft["json"]["id"]
        forked_published = self.records_cache.get(recid)
        cached_parent = self.parents_cache.get(parent["json"]["id"])
        if not cached_parent:
            self.parents_cache.add(
                parent["json"]["id"],  # recid
                {
                    "id": parent["id"],
                    "next_draft_id": draft["id"],
                },
            )
            # drafts have a parent on save
            # on the other hand there is no community parent/request
            yield from generate_parent_rows(parent)
        # if there is a parent (else) but there is no record it means that it is a
        # draft of a new version
        elif not forked_published:
            self.parents_cache.update(
                parent["json"]["id"],
                {
                    "next_draft_id": draft["id"],
                },
            )

        # if its a draft of a published record, its parent should be parent id
        # if its a new version, its parent should be the one of the previous version
        # otherwise is a new parent (new record, new draft...)
        parent_id = cached_parent["id"] if cached_parent else draft["parent_id"]
        if forked_published:
            parent_id = forked_published["parent_id"]

        yield RDMDraftMetadata(
            id=forked_published.get("id") or draft["id"],
            json=draft["json"],
            created=draft["created"],
            updated=draft["updated"],
            version_id=draft["version_id"],
            index=forked_published.get("index") or draft["index"],
            bucket_id=draft.get("bucket_id"),
            parent_id=parent_id,
            expires_at=draft["expires_at"],
            fork_version_id=forked_published.get("fork_version_id")
            or draft["fork_version_id"],
        )

        # if there is a record in the cache it means both recid and doi were already
        # processed in the records table generator, a duplicate would violate unique
        # constraints and cause the load to fail.
        if not forked_published:
            # recid
            record_pid = draft["json"]["pid"]
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
        # we don't emit doi Persistentidentifier for drafts as either they have already
        # one from records or have an external doi that is registered on publish

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

        def _resolve_pids(draft):
            """Enforce record pids to draft."""
            if not draft:
                return

            # some legacy records have different pid value in deposit than record
            # however _deposit.pid.value would contain the correct one
            # if it is not legacy we get it from the current field (json.id)
            recid = draft["json"]["id"]
            forked_published = self.records_cache.get(recid)
            if forked_published:
                pids = draft["json"]["pids"]
                has_draft_external_doi = (
                    pids.get("doi", {}).get("provider") == "external"
                )
                if has_draft_external_doi:
                    # then keep the draft external value as it might be there for
                    # updating the existing value. Update the draft only with `oai`
                    pids["oai"] = forked_published["pids"]["oai"]
                else:
                    # enfore published record pids to draft
                    pids = forked_published["pids"]

        # resolve parent communities slug
        parent = data["parent"]
        communities = parent["json"].get("communities")
        if communities:
            _resolve_communities(communities)
        _resolve_pids(data.get("draft"))

    # FIXME: deduplicate with records.py
    # assumis records post load alters pidstore_pid_id_seq and pidstore_recid_recid_seq
