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
from dataclasses import dataclass
from typing import ClassVar, Optional

import sqlalchemy.orm as orm

from invenio_rdm_migrator.extract.transactions import Tx

from ..logging import Logger
from ..transform import DatetimeMixin
from ..utils import dict_set


class Action:
    """Base action."""

    name = None

    def __init__(self):
        """Constructor."""
        assert self.name  # it must have a name


@dataclass
class LoadData:
    """Load action data."""

    tx: Optional[Tx]


class LoadAction(Action, ABC):
    """Load action.

    This generates the corresponding SQL operations to perform.
    """

    data_cls: ClassVar[type[LoadData]] = None
    pks = []

    def __init__(self, data: dict):
        """Constructor.

        :param pks: a triplet with the attribute, the key and the function.
        """
        assert data is not None
        data.setdefault("tx", None)
        self.data = self.data_cls(**data)
        super().__init__()

    def _generate_pks(self, session: orm.Session = None):
        for attr_name, path, pk_func in self.pks:
            try:
                attr = getattr(self.data, attr_name)
                if attr:
                    dict_set(attr, path, pk_func(attr))
            except AttributeError:
                logger = Logger.get_logger()
                logger.exception(f"Attribute {attr_name} not found", exc_info=1)
            except KeyError:
                logger = Logger.get_logger()
                logger.exception(f"Path {path} not found on record", exc_info=1)

    def _resolve_references(self, session: orm.Session = None, **kwargs):
        """Resolve references e.g communities slug names."""
        pass

    @abstractmethod
    def _generate_rows(self, session: orm.Session = None, **kwargs):
        """Yield generated rows."""

    def prepare(self, session: orm.Session, **kwargs):
        """Generate the SQL statements required to persist the action.

        Any required data should be part of the instance attributes.
        """
        # is_db_empty would come in play and make _generate_pks optional
        self._generate_pks(session=session)
        # resolve entry references
        self._resolve_references(session=session)
        yield from self._generate_rows(session=session, **kwargs)


class TransformAction(Action, DatetimeMixin, ABC):
    """Transform action.

    Detects/matches an action type based on transaction data and transforms the data
    into a target ``LoadAction``.
    """

    load_cls: ClassVar[type[LoadAction]] = None

    def __init__(self, tx: Tx):
        """Constructor."""
        assert self.load_cls is not None
        self.tx: Tx = tx
        super().__init__()

    def transform(self):
        """Transforms an action."""
        transformed_data = self._transform_data()
        transformed_data.pop("tx_id", None)
        transformed_data["tx"] = self.tx
        return self.load_cls(transformed_data)

    @abstractclassmethod
    def matches_action(cls, tx: Tx):  # pragma: no cover
        """Checks if the data matches with that required by the action."""

    @abstractmethod
    def _transform_data(self):  # pragma: no cover
        """Transforms the data and returns a dictionary."""
