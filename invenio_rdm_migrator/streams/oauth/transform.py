# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record transform interfaces."""

from ...transform import EncryptMixin, IdentityDictKeyMixin, Transform


class OAuthServerTokenTransform(Transform, IdentityDictKeyMixin):
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
        scopes = entry.get("_scopes", "").split(" ")
        new_scopes = []
        for scope in scopes:
            new_scope = self.SCOPES_MAPPING[scope]
            if new_scope:
                new_scopes.append(new_scope)

        return " ".join(new_scopes)

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "id": self._id(entry),
            "client_id": self._client_id(entry),
            "user_id": self._user_id(entry),
            "token_type": self._token_type(entry),
            "access_token": self._access_token(entry),
            "refresh_token": self._refresh_token(entry),
            "expires": self._expires(entry),
            "_scopes": self._scopes(entry),
            "is_personal": self._is_personal(entry),
            "is_internal": self._is_internal(entry),
        }


class OAuthRemoteTokenTransform(Transform, IdentityDictKeyMixin):
    """OAuth client remote token data transformation."""

    def _transform(self, entry):
        """Transform a single entry."""
        return {
            "id_remote_account": self._id_remote_account(entry),
            "token_type": self._token_type(entry),
            "access_token": self._access_token(entry),
            "secret": self._secret(entry),
            "created": self._created(entry),
            "updated": self._updated(entry),
        }
