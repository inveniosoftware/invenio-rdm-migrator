# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record transform interfaces."""

from ...transform import IdentityTransform


class OAuthServerTokenTransform(IdentityTransform):
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

    def _scopes(self, entry):
        """Token scopes."""
        scopes = entry.get("_scopes", "")

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

    def _transform(self, entry):
        """Transform a single entry."""
        data = super()._transform(entry)
        if data.get("_scopes"):
            data["_scopes"]: self._scopes(entry)

        return data


class OAuthRemoteTokenTransform(IdentityTransform):
    """OAuth client remote token data transformation."""

    # left as is to avoid breaking compatibility
    # behavior is the same
