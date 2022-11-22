# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 CERN.
#
# Invenio-RDM-Migrator is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Invenio RDM migration record load module."""

from ...transform import TableGenerator, PostgreSQLCopyLoad
from .tables import RDMRecordTableLoad, RDMVersionStateComputedTable


class RDMRecordCopyLoad(PostgreSQLCopyLoad):  # TODO: abstract SQL from PostgreSQL?
    """PostgreSQL COPY load."""

    def __init__(self, db_uri, output_path):
        """Constructor."""
        # used to keep track of what Parent IDs we've already inserted in the PIDs table.
        # {
        #     '<parent_pid>': {
        #         'id': <generated_parent_uuid>,
        #         'version': {
        #             'latest_index': 'record_index',
        #             'latest_id': 'record id',
        #         }
        # }
        self.parent_cache = {}
        super().__init__(
            db_uri=db_uri,
            output_path=output_path,
            table_loads = [
                RDMRecordTableLoad(self.parent_cache),
                RDMVersionStateComputedTable(self.parent_cache),
            ]
        )

    def _cleanup_db(self):
        """Cleanup DB after load."""
        # FIXME: abstract to tables, can we do without invenio imports
        # cant fix atm, versions state needs to be deleted in the middle
        # from invenio_db import db
        # from invenio_pidstore.models import PersistentIdentifier
        # from invenio_rdm_records.records.models import (
        #     RDMDraftMetadata,
        #     RDMParentMetadata,
        #     RDMRecordMetadata,
        #     RDMVersionsState,
        # )
        # PersistentIdentifier.query.filter(
        #     PersistentIdentifier.pid_type.in_(("recid", "doi", "oai")),
        #     PersistentIdentifier.object_type == "rec",
        # ).delete()
        # RDMVersionsState.query.delete()
        # RDMRecordMetadata.query.delete()
        # RDMParentMetadata.query.delete()
        # RDMDraftMetadata.query.delete()
        # db.session.commit()
        pass

    def _cleanup_files(self):
        """Cleanup files after load."""
        # FIXME: tables does not return the name correct
        # delegate to table_loads?
        # for table in self.tables:
        #     fpath = self.output_dir / f"{table._table_name}.csv"
        #     print(f"Checking {fpath}")
        #     if fpath.exists():
        #         print(f"Deleting {fpath}")
        #         fpath.unlink(missing_ok=True)
        pass
