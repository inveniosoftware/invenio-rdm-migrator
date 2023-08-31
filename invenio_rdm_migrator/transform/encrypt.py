# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transform interfaces."""

from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from ..state import STATE


class EncryptMixin:
    """Enables re-encryption of values based on old and new secret keys."""

    def __init__(self, *args, **kwargs):
        """Constructor."""
        state = STATE.VALUES
        old_secret_key = state.get("old_secret_key")["value"]
        assert old_secret_key
        self.decrypt_engine = self._init_engine(old_secret_key)

        new_secret_key = state.get("new_secret_key")["value"]
        assert new_secret_key
        self.encrypt_engine = self._init_engine(new_secret_key)
        super().__init__(*args, **kwargs)

    @staticmethod
    def _init_engine(secret_key):
        """Initialize an encryption engine."""
        engine = AesEngine()
        engine._update_key(secret_key)
        engine._set_padding_mechanism()

        return engine

    def re_encrypt(self, value):
        """Value re-encryption.

        Following invenio_db.utils:rebuild_encrypted_properties.
        This is the function used by invenio-oauthclient/oauth2server to re-encrypt
        when the secret key changes.
        It boils doen to sqlalchemy-utils AESEngine encrypt/decrypt.
        """
        decrypted_token = self.decrypt_engine.decrypt(value)
        new_value = self.encrypt_engine.encrypt(decrypted_token)

        return new_value
