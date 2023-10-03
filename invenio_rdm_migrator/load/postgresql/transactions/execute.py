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

from ....logging import FailedTxLogger, Logger
from ...base import Load
from .operations import OperationType


class PostgreSQLTx(Load):
    """PostgreSQL COPY load."""

    def __init__(
        self, db_uri, _session=None, dry=True, raise_on_db_error=False, **kwargs
    ):
        """Constructor."""
        self.db_uri = db_uri
        self.dry = dry
        self.raise_on_db_error = raise_on_db_error
        self._session = _session

    @property
    def session(self):
        """DB session."""
        if self._session is None:
            session_kwargs = dict(bind=create_engine(self.db_uri))
            if self.dry:
                session_kwargs["join_transaction_mode"] = "create_savepoint"
            self._session = Session(**session_kwargs)
        return self._session

    def _cleanup(self, db=False):
        """No cleanup."""
        logger = Logger.get_logger()
        logger.debug("PostgreSQLExecute does not implement _cleanup()")
        pass

    def _load(self, transactions):
        """Performs the operations of a group transaction."""
        logger = Logger.get_logger()
        failed_tx_logger = FailedTxLogger.get_logger()
        exec_kwargs = dict(execution_options={"synchronize_session": False})

        outer_trans = None
        if self.dry:
            outer_trans = self.session.begin()
        try:
            for action in transactions:
                with self.session.no_autoflush:
                    nested_trans = self.session.begin_nested()
                    try:
                        for op in action.prepare(session=self.session):
                            if op.type == OperationType.INSERT:
                                row = op.as_row_dict()
                                logger.info(f"INSERT {op.model}: {row}")
                                self.session.execute(
                                    sa.insert(op.model),
                                    [row],
                                    **exec_kwargs,
                                )
                            elif op.type == OperationType.DELETE:
                                logger.info(f"DELETE {op.model}: {op.data}")
                                self.session.execute(
                                    sa.delete(op.model).where(*op.pk_clauses),
                                    **exec_kwargs,
                                )
                            elif op.type == OperationType.UPDATE:
                                row = op.as_row_dict()
                                logger.info(f"UDPATE {op.model}: {op.data}")
                                self.session.execute(
                                    sa.update(op.model),
                                    [row],
                                    **exec_kwargs,
                                )
                            self.session.flush()
                        nested_trans.commit()
                    except Exception:
                        logger.exception(
                            f"Could not load {action.data} ({action.name})",
                            exc_info=True,
                        )
                        failed_tx_logger.exception(
                            "Failed processing transaction",
                            extra={"tx": action.data},
                            exc_info=True,
                        )
                        nested_trans.rollback()
                        if self.raise_on_db_error:
                            raise
        except Exception:
            logger.exception("Transactions load failed", exc_info=True)
            failed_tx_logger.exception("Failed transaction", exc_info=True)
            if self.raise_on_db_error:
                # NOTE: the "finally" block below will run before this "raise"
                raise
        finally:
            if self.dry and outer_trans:
                outer_trans.rollback()

    def run(self, entries, cleanup=False):
        """Load entries."""
        self._load(entries)
