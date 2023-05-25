# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record table load module."""

from datetime import datetime
from functools import partial

import psycopg

from ....load.ids import generate_recid, generate_uuid, pid_pk
from ....load.models import PersistentIdentifier
from ....load.postgresql import TableGenerator
from ...files.models import FilesObjectVersion
from ..models import RDMDraftFile, RDMDraftMetadata, RDMParentMetadata
from .parents import generate_parent_rows


class RDMDraftTableGenerator(TableGenerator):
    """RDM Record and related tables load."""

    def __init__(self, parents_state, records_state, communities_state):
        """Constructor."""
        super().__init__(
            tables=[
                RDMDraftMetadata,
                RDMParentMetadata,
                PersistentIdentifier,
            ],
            post_load_hooks=[self.insert_draft_files],
            pks=[
                ("draft.id", generate_uuid),
                ("parent.id", generate_uuid),
                ("draft.json.pid", partial(generate_recid, status="N")),
                ("parent.json.pid", generate_recid),
                ("draft.parent_id", lambda d: d["parent"]["id"]),
            ],
        )
        self.parents_state = parents_state
        self.records_state = records_state
        self.communities_state = communities_state

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
        forked_published = self.records_state.get(recid)
        state_parent = self.parents_state.get(parent["json"]["id"])
        if not state_parent:
            self.parents_state.add(
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
            self.parents_state.update(
                parent["json"]["id"],
                {
                    "next_draft_id": draft["id"],
                },
            )

        # if its a draft of a published record, its parent should be parent id
        # if its a new version, its parent should be the one of the previous version
        # otherwise is a new parent (new record, new draft...)
        parent_id = state_parent["id"] if state_parent else draft["parent_id"]
        if forked_published:
            parent_id = forked_published["parent_id"]

        yield RDMDraftMetadata(
            id=forked_published.get("id") or draft["id"],
            json=draft["json"],
            created=draft["created"],
            updated=draft["updated"],
            version_id=draft["version_id"],
            index=forked_published.get("index") or draft["index"],
            bucket_id=draft["bucket_id"],
            parent_id=parent_id,
            expires_at=draft["expires_at"],
            fork_version_id=forked_published.get("fork_version_id")
            or draft["fork_version_id"],
        )

        # if there is a record in the state it means both recid and doi were already
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
        # draft files are a post_hook

    # FIXME: deduplicate with records.py
    def _resolve_references(self, data, **kwargs):
        """Resolve references e.g communities slug names."""

        def _resolve_communities(communities):
            default_slug = communities.get("default")
            default_id = self.communities_state.get(default_slug)
            if not default_id:
                # TODO: maybe raise error without correct default community?
                communities = {}

            communities["default"] = default_id

            communities_slugs = communities.get("ids", [])
            _ids = []
            for slug in communities_slugs:
                _id = self.communities_state.get(slug)
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
            forked_published = self.records_state.get(recid)
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

    def insert_draft_files(self, db_uri=None):
        """Inserts draft files from buckets and object version."""
        assert db_uri  # should have come from kwargs

        with psycopg.connect(db_uri) as conn:
            # the query needs to be split in 3 parts because the empty jsonb dict
            # would cause problems with the string formatting
            insert = f"""
                INSERT INTO {RDMDraftFile._table_name} (
                    id, json, created, updated, version_id, key, record_id, object_version_id
                )
            """
            select = "SELECT gen_random_uuid(), '{}'::jsonb, rdm.created, rdm.updated, 1, fo.key, rdm.id, fo.version_id"
            from_and_join = f"""
                FROM {RDMDraftMetadata._table_name} AS rdm
                INNER JOIN {FilesObjectVersion._table_name} AS fo
                ON rdm.bucket_id=fo.bucket_id AND fo.is_head='true'
            """
            # no return check, will raise if the sql statement fails
            # id and json do not have defaults in DB even though if the programmatic
            # models have them, so they need to be calculated
            conn.execute(insert + select + from_and_join)
