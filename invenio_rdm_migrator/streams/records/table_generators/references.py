# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM records table generators references."""

from ....state import STATE


class CommunitiesReferencesMixin:
    """Communities reference resolver."""

    def resolve_communities(self, communities):
        """Translates communities slugs to ids.

        Assumes the the table generator has a communities_state attribute.
        """
        default_slug = communities.get("default")
        default_id = STATE.COMMUNITIES.get(default_slug)
        if not default_id:
            # raise error without correct default community?
            communities = {}

        communities["default"] = default_id

        communities_slugs = communities.get("ids", [])
        _ids = []
        for slug in communities_slugs:
            _id = STATE.COMMUNITIES.get(slug)
            if _id:
                _ids.append(_id)
        communities["ids"] = _ids


class PIDsReferencesMixin:
    """PIDs reference resolver."""

    def resolve_draft_pids(self, draft):
        """Enforce record pids to draft."""
        if not draft:
            return

        # some legacy records have different pid value in deposit than record
        # however _deposit.pid.value would contain the correct one
        # if it is not legacy we get it from the current field (json.id)
        recid = draft["json"]["id"]
        forked_published = STATE.RECORDS.get(recid)
        if forked_published:
            pids = draft["json"]["pids"]
            has_draft_external_doi = pids.get("doi", {}).get("provider") == "external"
            if has_draft_external_doi:
                # then keep the draft external value as it might be there for
                # updating the existing value. Update the draft only with `oai`
                pids["oai"] = forked_published["pids"]["oai"]
            else:
                # enfore published record pids to draft
                pids = forked_published["pids"]
