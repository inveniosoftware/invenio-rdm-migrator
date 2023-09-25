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

    def __init__(self, db_uri, _session=None, dry=True, raise_on_db_error=False, **kwargs):
        """Constructor."""
        self.db_uri = db_uri
        self.dry = dry
        self.raise_on_db_error = raise_on_db_error
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

    def _load(self, transactions):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()
        exec_kwargs = dict(execution_options={"synchronize_session": False})

        for action in transactions:
            operations = []
            try:
                operations = list(action.prepare())
            except Exception:
                logger.exception(
                    f"Could not load {action.data} ({action.name})",
                    exc_info=1,
                )

            with self.session.begin(), self.session.no_autoflush:
                try:
                    for op in operations:
                        if op.type == OperationType.INSERT:
                            row = op.as_row_dict()
                            logger.info(f"INSERT {op.model}: {row}")
                            if not self.dry:
                                self.session.execute(
                                    sa.insert(op.model),
                                    [row],
                                    **exec_kwargs,
                                )
                        elif op.type == OperationType.DELETE:
                            logger.info(f"DELETE {op.model}: {op.data}")
                            if not self.dry:
                                self.session.execute(
                                    sa.delete(op.model).where(*op.pk_clauses),
                                    **exec_kwargs,
                                )
                        elif op.type == OperationType.UPDATE:
                            row = op.as_row_dict()
                            logger.info(f"UDPATE {op.model}: {op.data}")
                            if not self.dry:
                                self.session.execute(
                                    sa.update(op.model),
                                    [row],
                                    **exec_kwargs,
                                )
                        if not self.dry:
                            self.session.flush()
                        else:
                            self.session.expunge_all()
                    # commit all transaction group or none
                    if not self.dry:
                        self.session.commit()
                except Exception as ex:
                    logger.exception(
                        f"Could not load {action.data} ({action.name}), {ex}",
                        exc_info=True,
                    )
                    if not self.dry:
                        self.session.rollback()
                    if self.raise_on_db_error:
                        raise

    def run(self, entries, cleanup=False):
        """Load entries."""
        self._load(entries)
