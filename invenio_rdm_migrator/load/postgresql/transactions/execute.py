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

    def _update_obj(self, session, obj):
        """Updates all attributes of an object."""
        # this function accesses many private methods, variables, assumes indexes, etc.
        # pragmatic implementation, feel free to refactor.
        pk = obj.__mapper__.primary_key[0].name
        pk_value = getattr(obj, pk)
        db_obj = session.get(obj.__class__, pk_value)
        for column in db_obj.__table__.columns.keys():
            value = getattr(obj, column)
            setattr(db_obj, column, value)

        return obj

    def _load(self, transactions):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()

        for action in transactions:
            operations = action.prepare()

            with Session(self._engine) as session:
                for op in operations:
                    type_ = op.type
                    obj = op.obj
                    try:
                        if type_ == OperationType.INSERT:
                            session.add(obj)
                        elif type_ == OperationType.DELETE:
                            session.delete(obj)
                        elif type_ == OperationType.UPDATE:
                            self._update_obj(session, obj)
                        session.flush()
                    except Exception:
                        logger.exception(
                            f"Could not load {action.tx_id} ({action.name})",
                            exc_info=1,
                        )
                        session.rollback()
                        raise
                # commit all transaction group or none
                session.commit()

    def run(self, entries, cleanup=False):
        """Load entries."""
        self._load(entries)
