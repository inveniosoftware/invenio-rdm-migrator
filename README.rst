..
    Copyright (C) 2022-2023 CERN.


    Invenio-RDM-Migrator is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

=====================
 Invenio-RDM-Migrator
=====================

.. image:: https://github.com/inveniosoftware/invenio-rdm-migrator/workflows/CI/badge.svg
        :target: https://github.com/inveniosoftware/invenio-rdm-migrator/actions?query=workflow%3ACI+branch%3Amaster

.. image:: https://img.shields.io/github/tag/inveniosoftware/invenio-rdm-migrator.svg
        :target: https://github.com/inveniosoftware/invenio-rdm-migrator/releases

.. image:: https://img.shields.io/pypi/dm/invenio-rdm-migrator.svg
        :target: https://pypi.python.org/pypi/invenio-rdm-migrator

.. image:: https://img.shields.io/github/license/inveniosoftware/invenio-rdm-migrator.svg
        :target: https://github.com/inveniosoftware/invenio-rdm-migrator/blob/master/LICENSE

DataCite-based data model for Invenio.


Development
===========

Install
-------

Make sure that you have `libpq-dev` installed in your system. See
`psycopg installation instructions <https://www.psycopg.org/install/>`_
for more information.

Choose a version of search and database, then run:

.. code-block:: console

    pip install -e .


Tests
-----

.. code-block:: console

    ./run-tests.sh

How to run it
=============

To run the migration you need:

- A running InvenioRDM instance.
- If your data contains references to other records (e.g. vocabularies),
  then it is also required to run the setup step.

.. code-block:: console

    invenio-cli services setup --force --no-demo-data

- Install Invenio-RDM-Migrator, any other dependencies must be handled
  in the Pipfile of your instance.

.. code-block:: console

    $ pip install invenio-rdm-migrator

- Create/edit the configuration file on your instance, for example
  `streams.yaml`:

.. code-block:: yaml

    data_dir: /path/to/data
    tmp_dir: /path/to/tmp
    state_dir: /path/to/state
    log_dir: /path/to/logs
    db_uri: postgresql+psycopg2://inveniordm:inveniordm@localhost:5432/inveniordm
    old_secret_key: CHANGE_ME
    new_secret_key: CHANGE_ME
    records:
        extract:
            filename: /path/to/records.json


- You will need to create a small python script
  putting together the different blocks of the ETL. You can find an eample
  at `my-site/site/my_site/migrator/__main__.py`.

.. code-block:: python

    from invenio_rdm_migrator.streams import StreamDefinition
    from invenio_rdm_migrator.streams.records import RDMRecordCopyLoad

    if __name__ == "__main__":
        RecordStreamDefinition = StreamDefinition(
            name="records",
            extract_cls=JSONLExtract,
            transform_cls=ZenodoToRDMRecordTransform,
            load_cls=RDMRecordCopyLoad,
        )

        runner = Runner(
            stream_definitions=[
                RecordStreamDefinition,
            ],
            config_filepath="path/to/your/streams.yaml",
        )

        runner.run()

- Finally, you can execute the above code. Since it is in the `__main__` file
  of the python package, you can run it as a module:

.. code-block:: console

    $ python -m my_site.migrator

- Once the migration has completed, in your instance you can reindex the data.
  Following the records example above, it would look like:

.. code-block:: console

    $ invenio-cli pyshell

    In [1]: from invenio_access.permissions import system_identity
    In [2]: from invenio_rdm_records.proxies import current_rdm_records_service
    In [3]: current_rdm_records_service.rebuild_index(identity=system_identity)

ETL {Extract/Transform/Load} architecture
=========================================

There are four packages in this module `extract`, `transform`, `load`, and
`streams`. The first three correspond to the three steps of an ETL process.
The `streams` package contains the logic to run the process and different
stream-specific implementations of ETL classes (e.g. `records`).

Extract
-------

The extract is the first part of the data processing stream. It's
functionality is quite simple: return an iterator (e.g. of records), where each
yielded value is a dictionary. Note that the data in this step is _transformed_
in format (e.g. JSON, XML), not in content. For example, the implementation of
`XMLExtract` would look as follows:

.. code-block:: python

    class XMLExtract(Extract):
    ...

        def run(self):
            with open("file.xml") as file:
                for entry in file:
                    yield xml.loads(entry)

Transform
---------

The transformer is in charge of modifying the content to suit, in this case,
the InvenioRDM data model (e.g. for records) so it can be imported in the DB.
It will loop through the entries (i.e. the iterator returned by the extract
class), transform and yield (e.g. the record). Diving more in the example of
a record:

To transform something to an RDM record, you need to implement
`streams/records/transform.py:RDMRecordTransform`. For each record it will
yield what is considered a semantically "full" record: the record itself,
its parent, its draft in case it exists and the files related them.

.. code-block:: python

    {
        "record": self._record(entry),
        "draft": self._draft(entry),
        "parent": self._parent(entry),
    }

This means that you will need to implement the functions for each key. Note
that, only `_record` and `_parent` should return content, the others can return
`None`.

Some of these functions can themselves use a `transform/base:Entry`
transformer. An _entry_ transformer is an extra layer of abstraction, to
provide an interface with the methods needed to generate valid data for part of
the `Transform` class. In the record example, you can implement
`transform.base:RDMRecordEntry`, which can be used in the
`RDMRecordTransform._record` function mentioned in the code snippet above. Note
that implementing this interface will produce valid _data_ for a record.
However, there is no abc for _metadata_. It is an open question how much we
should define these interfaces and avoid duplicating the already existing
Marshmallow schemas of InvenioRDM.

At this point you might be wondering "Why not Marshmallow then?". The answer is
"separation of responsibilities, performance and simplicity". The later lays
with the fact that most of the data transformation is custom, so we would end
up with a schema full of `Method` fields, which does not differ much from what
we have but would have an impact on performance (Marshmallow is slow...).
Regarding the responsibilities part, validating (mostly referential, like
vocabularies) can only be done on (or after) _load_ where RDM instance knowledge/appctx
is available.

Note that no validation, not even structural, is done in this step.

Load
----

The final step to have the records available in the RDM instance is to load
them. There are two types of loading _bulk_ or _transactions_.

Bulk
....

Bulk loading will insert data in the database table by table using `COPY`. Since
the order of the tables is not guaranteed it is necessary to drop foreign keys before
loading. They can be restored afterwards. In addition, dropping indices would increase
performance since they will only be calculated once, when they are restored after loading.

Bulk loading is done using the `load.postgresql.bulk:PostgreSQLCopyLoad` class, which will
carry out 2 steps:

1. Prepare the data, writing one DB row per line in a csv file:

.. code-block:: console

    $ /path/to/data/tables1668697280.943311
        |
        | - pidstore_pid.csv
        | - rdm_parents_metadata.csv
        | - rdm_records_metadata.csv
        | - rdm_versions_state.csv

2. Perform the actual loading, using `COPY`. Inserting all rows at once is more
   efficient than performing one `INSERT` per row.

Internally what is happening is that the `prepare` function makes use of
`TableGenerator` implementations and then yields the list of csv files.
So the `load` only iterates through the filenames, not the actual entries.

A `TableGenerator` will, for each value in the iterator, yield one
or more rows (lines to be written to the a csv file). For example for a record
it will yield: recid, DOI and OAI (PersistentIdentifiers), record and parent
metadata, etc. which will be written to the respective CSV file.


Transactions
............

Another option is to migrate transactions. For example, once you have done the initial
part of it in bulk, you can migrate the changes that were persisted while the bulk
migration happened. That can be achieved by migrating transactions. A transaction is a
group of operations, which can be understod as SQL statement and thus have two values:
the operation type (created, update, delete) and its data represented as a database model.

Transaction loading is done using the `load.postgresql.transactions:PostgreSQLExecuteLoad`
class, which will carry out 2 similar steps to the one above:

1. Prepare the data, storing in memory a series of `Operation`\s.
2. Perform the actual loading by adding or removing from the session, or updating the
   corresponding object. Each operation is flushed to the database to avoid foreing key
   violations. However, each transaction is atomic, meaning that an error in one of the
   operations will cause the full transaction to fail as a group.

Internally, the load will use an instance of
`load.postgresql.transactions.generators.group:TxGenerator` to prepare the
operations. This class contains a mapping between table names and
`load.postgresql.transactions.generators.row:RowGenerators`, which will return a list of
operations with the data as database model in the `obj` attribute.

Note that the `TxGenerator` is tightly coupled to the
`transform.transactions.Tx` since it expects the dictionaries to have a
specific structure:

.. code-block::

    {
        "tx_id": the actual transaction id, useful for debug and error handling
        "action": this information refers to the semantic meaning of the group
                       for example: record metadata update or file upload
        "operations": [
            {
                "op": c (create), u (update), d (delete)
                "table": the name of the table in the source system (e.g. Zenodo)
                "data": the transformed data, this can use any `Transform` implementation
            }
        ]
    }

State
=====

During a migration run, there is a need to share information across different streams
or different generators on the same stream. For example, the records stream needs to
access the UUID to slug map that was populated on the communities stream; or the
drafts generator needs to know which parent records have been created on the records
generator to keep the version state consistent.

All this information is persisted to a SQLite database. This state database is kept
in memory during each stream processing, and it is persisted to disk if the stream
finishes without errors. The state will be saved with the name of the stream
(e.g. `records.db`) to avoid overwriting a previous state. Therefore, a migration can be
restarted from any stream.

There are two ways to add more information to the state:

- Full entities, for example record or users, require their own DB table. Those must be
  defined at `state.py:State._initialize_db`. In addition, to abstract the access to that
  table, a state entity is required. It needs to be initialized in the `Runner.py:Runner`
  constructor and added the the `state_entities` dictionary.
- Independent value, for example the maximum value of generated primary keys. Those can be
  stored in the `global_state`. This state has two columns: key and value; adding
  information to it would look like `{key: name_of_the_value, value: actual_value}`.

Notes
=====

**Using python generators**

Using generators instead of lists, allows us to iterate through the data
only once and perform the E-T-L steps on them. Instead of loop for E, loop
for T, loop for L. In addition, this allows us to have the csv files open
during the writing and closing them at the end (open/close is an expensive
op when done 3M times).
