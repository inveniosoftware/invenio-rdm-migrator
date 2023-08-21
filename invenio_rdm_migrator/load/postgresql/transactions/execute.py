# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL Execute load."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ....logging import Logger
from ...base import Load
from .operations import OperationType


class PostgreSQLTx(Load):
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, _session=None, **kwargs):
        """Constructor."""
        self.db_uri = db_uri
        self._session = _session

    @property
    def _engine(self):
        if self._engine is None:
            self._engine = create_engine(self.db_uri)
        return self._engine

    @property
    def session(self):
        """DB session."""
        if self._session is None:
            self._session = Session(bind=self._engine)
        return self._session

    def _cleanup(self, db=False):
        """No cleanup."""
        logger = Logger.get_logger()
        logger.debug("PostgreSQLExecute does not implement _cleanup()")
        pass

    def _get_obj_by_pk(self, model, data):
        """Get an object based on the primary key."""
        # this function accesses many private methods, variables, assumes indexes, etc.
        # pragmatic implementation, feel free to refactor.
        pk = {}
        for key in model.__mapper__.primary_key:
            pk[key.name] = data[key.name]

        return self.session.get(model, pk)

    def _load(self, transactions):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()

        for action in transactions:
            operations = action.prepare()
            with self.session.begin():
                for op in operations:
                    try:
                        if op.type == OperationType.INSERT:
                            obj = op.model(**op.data)
                            self.session.add(obj)
                        elif op.type == OperationType.DELETE:
                            obj = self._get_obj_by_pk(op.model, op.data)
                            self.session.delete(obj)
                        elif op.type == OperationType.UPDATE:
                            obj = self._get_obj_by_pk(op.model, op.data)
                            # due to dictdiff/partial updates we only update those
                            # keys that changed the value. there is no instantiation
                            # of the data class with the op.data so they dont need
                            # values to be defined as optional
                            for key, value in op.data.items():
                                setattr(obj, key, value)

                        self.session.flush()
                    except Exception:
                        logger.exception(
                            f"Could not load {action.data.tx_id} ({action.name})",
                            exc_info=1,
                        )
                        self.session.rollback()
                        raise
                # commit all transaction group or none
                self.session.commit()

    def run(self, entries, cleanup=False):
        """Load entries."""
        self._load(entries)
