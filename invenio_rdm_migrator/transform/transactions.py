# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration transaction transform."""

from abc import ABC

from ..actions.base import TransformAction
from .base import Transform


class BaseTxTransform(Transform, ABC):
    """Transform a transaction."""

    actions: list[TransformAction] = []

    def _detect_action(self, tx):
        for action_cls in self.actions:
            if action_cls.matches_action(tx):
                return action_cls  # return the first matched class

    def _transform(self, tx):
        """Transform action.

        Each action contains the raw transaction data.
        :returns: an instance of LoadAction.
        """
        action_cls = self._detect_action(tx)
        if not action_cls:
            raise Exception(f"Could not detect action for {tx}")

        action = action_cls(tx)
        return action.transform()
