# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""PostgreSQL Execute load."""

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from ....logging import Logger
from ...base import Load
from .operations import OperationType


class PostgreSQLTx(Load):
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, _session=None, dry=True, **kwargs):
        """Constructor."""
        self.db_uri = db_uri
        self.dry = dry
        self._session = _session

    @property
    def session(self):
        """DB session."""
        if self._session is None:
            self._session = Session(bind=create_engine(self.db_uri))
        return self._session

    def _cleanup(self, db=False):
        """No cleanup."""
        logger = Logger.get_logger()
        logger.debug("PostgreSQLExecute does not implement _cleanup()")
        pass

    def _get_obj_pk(self, model, data):
        """Get an object's primary key as a dict."""
        return {col.name: data[col.name] for col in model.__mapper__.primary_key}

    def _get_obj_pk_clauses(self, model, data):
        """Get an object's primary key as a dict."""
        return [col == data[col.name] for col in model.__mapper__.primary_key]

    def _get_obj_by_pk(self, model, data):
        """Get an object based on the primary key."""
        return self.session.get(model, self._get_obj_pk(model, data))

    def _load(self, transactions):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()
        exec_kwargs = dict(execution_options={"synchronize_session": False})

        for action in transactions:
            operations = action.prepare()
            with self.session.begin(), self.session.no_autoflush:
                for op in operations:
                    try:
                        if op.type == OperationType.INSERT:
                            self.session.execute(
                                sa.insert(op.model),
                                [op.data],
                                **exec_kwargs,
                            )
                        elif op.type == OperationType.DELETE:
                            pk_clauses = self._get_obj_pk_clauses(op.model, op.data)
                            self.session.execute(
                                sa.delete(op.model).where(*pk_clauses),
                                **exec_kwargs,
                            )
                        elif op.type == OperationType.UPDATE:
                            self.session.execute(
                                sa.update(op.model),
                                [op.data],
                                **exec_kwargs,
                            )
                        if not self.dry:
                            self.session.flush()
                        else:
                            self.session.expunge_all()
                    except Exception:
                        logger.exception(
                            f"Could not load {action.data.tx_id} ({action.name}): {op}",
                            exc_info=1,
                        )
                        if not self.dry:
                            self.session.rollback()
                        raise
                # commit all transaction group or none
                if not self.dry:
                    self.session.commit()

    def run(self, entries, cleanup=False):
        """Load entries."""
        self._load(entries)
