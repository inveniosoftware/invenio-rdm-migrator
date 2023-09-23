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
from .errors import MultipleActionMatches, NoActionMatch


class BaseTxTransform(Transform, ABC):
    """Transform a transaction."""

    actions: list[TransformAction] = []

    def _detect_action(self, tx):
        match_classes = []
        for action_cls in self.actions:
            if action_cls.matches_action(tx):
                match_classes.append(action_cls)

        if len(match_classes) == 0:
            raise NoActionMatch(tx)
        elif len(match_classes) > 1:
            raise MultipleActionMatches(tx, match_classes)

        return match_classes[0]  # return the one and only matched class

    def _transform(self, tx):
        """Transform action.

        Each action contains the raw transaction data.
        :returns: an instance of LoadAction.
        """
        action_cls = self._detect_action(tx)
        action = action_cls(tx)
        return action.transform()
