# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record transform interfaces."""

from ...transform import IdentityTransform


class OAuthServerScopesMapMixin:
    """OAuth server token data transformation."""

    SCOPES_MAPPING = {
        "deposit:actions": None,
        "deposit:extra_formats": None,
        "deposit:write": None,
        "generate": "tokens:generate",
        "user:email": "user:email",
        "webhooks:event": "webhooks:event",
    }
    """Keys are Invenio v3 scopes and values are new RDM scopes."""

    def map_scopes(self, scopes):
        """Token scopes."""
        scopes = scopes or ""

        if scopes:  # account for cases where scopes = "", otherwise scopes = [""] fails
            scopes = scopes.split(" ")
        else:
            return ""

        new_scopes = []
        for scope in scopes:
            new_scope = self.SCOPES_MAPPING[scope]
            if new_scope:
                new_scopes.append(new_scope)

        return " ".join(new_scopes)


class OAuthServerTokenTransform(IdentityTransform, OAuthServerScopesMapMixin):
    """Transform OAuth server token."""

    def _transform(self, entry):
        """Transform a single entry."""
        data = super()._transform(entry)
        scopes = data.get("_scopes")
        if scopes:
            data["_scopes"] = self.map_scopes(scopes)
        return data


class OAuthServerClientTransform(IdentityTransform, OAuthServerScopesMapMixin):
    """Transform OAuth server client."""

    def _transform(self, entry):
        """Transform a single entry."""
        data = super()._transform(entry)
        scopes = data.get("_default_scopes")
        if scopes:
            data["_default_scopes"] = self.map_scopes(scopes)
        return data
