# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Identity transformation tests."""

import pytest
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine

from invenio_rdm_migrator.transform import EncryptMixin, Transform


@pytest.fixture(scope="function")
def secret_keys_state(state):
    """Adds secret keys to global state."""
    state.VALUES.add(
        "old_secret_key",
        {"value": bytes("OLDKEY", "utf-8")},
    )
    state.VALUES.add(
        "new_secret_key",
        {"value": bytes("NEWKEY", "utf-8")},
    )
    return


@pytest.fixture(scope="function")
def transform_with_mixin():
    """Test instance of a transform class with identity mixin"""

    class FixtureTransform(Transform, EncryptMixin):
        """Transform fixture class."""

        def _token(self, entry):
            return self.re_encrypt(entry["token"])

        def _transform(self, entry):
            """Transform entry."""
            return {
                "token": self._token(entry),
            }

    return FixtureTransform()


def test_encrypt_transform(secret_keys_state, transform_with_mixin):
    token = "itsasecret"

    encrypt_engine = AesEngine()
    encrypt_engine._update_key(bytes("OLDKEY", "utf-8"))
    encrypt_engine._set_padding_mechanism()

    encrypted_token = encrypt_engine.encrypt(token)

    t_item = transform_with_mixin._transform({"token": encrypted_token})
    t_token = t_item["token"]

    assert t_token != token != encrypted_token

    decrypt_engine = AesEngine()
    decrypt_engine._update_key(bytes("NEWKEY", "utf-8"))
    decrypt_engine._set_padding_mechanism()

    assert decrypt_engine.decrypt(t_token) == token
