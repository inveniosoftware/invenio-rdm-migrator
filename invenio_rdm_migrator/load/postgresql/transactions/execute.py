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

    def __init__(self, db_uri, tx_generator, **kwargs):
        """Constructor."""
        self.db_uri = db_uri
        self._engine = create_engine(self.db_uri)
        # an instance of TableGeneratorMapper
        self.txg = tx_generator

    def _cleanup(self, db=False):
        """No cleanup."""
        logger = Logger.get_logger()
        logger.debug("PostgreSQLExecute does not implement _cleanup()")
        pass

    def _prepare(self, entry):
        """Identify transaction group and generate the corresponding op-data pairs."""
        _operations = []
        for op in entry["operations"]:
            ops = self.txg.prepare(
                op["table"], OperationType(op["op"].upper()), op["data"]
            )
            if ops:
                _operations.extend(ops)

        entry["operations"] = _operations

        return entry

    def _update_obj(self, session, obj):
        """Updates all attributes of an object."""
        # FIXME: this function accesses many private methods, variables
        # assumes indexes, etc. Needs refactoring, implemented for PoC
        pk = obj.__mapper__.primary_key[0].name
        pk_value = getattr(obj, pk)
        db_obj = session.get(obj.__class__, pk_value)
        for column in db_obj.__table__.columns.keys():
            value = getattr(obj, column)
            setattr(db_obj, column, value)

        return obj

    def _load(self, tx):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()

        with Session(self._engine) as session:
            for op in tx["operations"]:
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
                        f"Could not {tx['tx_id']} ({tx['action']})",
                        exc_info=1,
                    )
                    session.rollback()
                    raise
            # commit all transaction group or none
            session.commit()
