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

    def __init__(self, db_uri, **kwargs):
        """Constructor."""
        self.db_uri = db_uri
        self._engine = create_engine(self.db_uri)

    def _cleanup(self, db=False):
        """No cleanup."""
        logger = Logger.get_logger()
        logger.debug("PostgreSQLExecute does not implement _cleanup()")
        pass

    def _get_obj_by_pk(self, session, model, data):
        """Get an object based on the primary key."""
        # this function accesses many private methods, variables, assumes indexes, etc.
        # pragmatic implementation, feel free to refactor.
        pk = {}
        for key in model.__mapper__.primary_key:
            pk[key.name] = data[key.name]

        return session.get(model, pk)

    def _load(self, transactions):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()

        for action in transactions:
            operations = action.prepare()

            with Session(self._engine) as session:
                for op in operations:
                    try:
                        if op.type == OperationType.INSERT:
                            obj = op.model(**op.data)
                            session.add(obj)
                        elif op.type == OperationType.DELETE:
                            obj = self._get_obj_by_pk(session, op.model, op.data)
                            session.delete(obj)
                        elif op.type == OperationType.UPDATE:
                            obj = self._get_obj_by_pk(session, op.model, op.data)
                            for key, value in op.data.items():
                                setattr(obj, key, value)

                        session.flush()
                    except Exception:
                        logger.exception(
                            f"Could not load {action.data.tx_id} ({action.name})",
                            exc_info=1,
                        )
                        session.rollback()
                        raise
                # commit all transaction group or none
                session.commit()

    def run(self, entries, cleanup=False):
        """Load entries."""
        self._load(entries)
