# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Base action module.

In the table generator approach, the E T L classes contain the logic to process the
entries. When using actions the responsibility is shifted to these classes, making
the E T L instances a lightweight container that "calls" the corresponding method on
an action. Being the latter the one implementing the logic.
"""

from abc import ABC, abstractclassmethod, abstractmethod

from ..logging import Logger
from ..utils import dict_set


class Action:
    """Base action."""

    name = None

    def __init__(self, tx_id):
        """Constructor."""
        assert self.name  # it must have a name
        self.tx_id = tx_id


class TransformAction(Action, ABC):
    """Transform action.

    This action detects or fingerprints an action type based on data and enables its
    transformation into a LoadAction.
    """

    mapped_cls = None

    def __init__(self, tx_id, data):
        """Constructor."""
        super().__init__(tx_id=tx_id)
        assert isinstance(data, list)  # list of dictionaries with payload
        self.data = data

    def transform(self):
        """Transforms an action."""
        return self.mapped_cls(tx_id=self.tx_id, **self._transform_data())

    def fingerprint(self):  # pragma: no cover
        """Checks if the data corresponds with that required by the action.

        If it does, it sets the attributes.
        """
        return False

    @abstractmethod
    def _transform_data(self):  # pragma: no cover
        """Transforms the data and returns an instance of the mapped_cls."""


class LoadAction(Action, ABC):
    """Load action.

    This generates the corresponding SQL operations to perform.
    """

    def __init__(self, tx_id, pks=None):
        """Constructor.

        :param pks: a triplet with the attribute, the key and the function.
        """
        super().__init__(tx_id)
        self.pks = pks or []

    def _generate_pks(self):
        for attr_name, path, pk_func in self.pks:
            try:
                attr = getattr(self, attr_name)
                dict_set(attr, path, pk_func(attr))
            except AttributeError:
                logger = Logger.get_logger()
                logger.exception(f"Attribute {attr_name} not found", exc_info=1)
            except KeyError:
                logger = Logger.get_logger()
                logger.exception(f"Path {path} not found on record", exc_info=1)

    def _resolve_references(self, data, **kwargs):  # pragma: no cover
        """Resolve references e.g communities slug names."""
        pass

    @abstractmethod
    def _generate_rows(self, **kwargs):  # pragma: no cover
        """Yield generated rows."""

    def prepare(self, **kwargs):
        """Generate the SQL statements required to persist the action.

        Any required data should be part of the instance attributes.
        """
        # is_db_empty would come in play and make _generate_pks optional
        self._generate_pks()
        # resolve entry references
        self._resolve_references()
        yield from self._generate_rows(**kwargs)
