# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration OAuth stream."""

from .load import OAuthClientCopyLoad, OAuthServerCopyLoad
from .transform import OAuthRemoteTokenTransform, OAuthServerTokenTransform

__all__ = (
    "OAuthClientCopyLoad",
    "OAuthRemoteTokenTransform",
    "OAuthServerCopyLoad",
    "OAuthServerTokenTransform",
)
