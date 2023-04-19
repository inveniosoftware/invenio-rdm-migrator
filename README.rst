..
    Copyright (C) 2022 CERN.


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

    records:
        extract:
            filename: /path/to/records.json
        load:
            db_uri: postgresql+psycopg2://inveniordm:inveniordm@localhost:5432/inveniordm
            tmp_dir: /tmp/migrator


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
  For example, for users and records it would look like:

.. code-block:: console

    $ invenio-cli pyshell

    In [1]: from invenio_access.permissions import system_identity
    In [2]: from invenio_rdm_records.proxies import current_rdm_records_service
    In [3]: from invenio_users_resources.proxies import current_users_service

    In [4]: current_users_service.rebuild_index(identity=system_identity)
    In [5]: current_rdm_records_service.rebuild_index(identity=system_identity)

Implement your {Extract/Transform/Load}
=======================================

There are for packages in this module `extract`, `transform`, `load`, and
`streams`. The first three correspond to the three steps of an ETL process.
The `streams` package contains the logic to run the process and different
stream-specific implementations of ETL classes (e.g. `records`).

Extract
-------

The extract is the first part of the data processing stream. It's
functionality is quite simple: return an iterator (e.g. of records), where each
yielded value is a dictionary. Note that the data in this step is _transformed_
to an extent, but only in format (e.g. JSON, XML), not in content. For example,
to implement a `XMLExtract` class:

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
`None`. In this case we will need to re-think which methods should be
`abstractmethod` and which ones be defaulted to `None/{}/some other default` in
the base. You can find an example implementation at
`zenodo-rdm/site/zenodo_rdm/migrator/transform.py:ZenodoToRDMRecordTransform`.

Some of these functions can themselves use a `transform/base:Entry`
transformer. An _entry_ transformer is a one layer deeper abstraction, to
provide an interface with the methods needed to generate valid data for part of
the `Transform` class. In the record example, you can implement
`transform.base:RDMRecordEntry`, which can be used in the
`RDMRecordTransform._record` function mentioned in the code snippet above. Note
that implementing this interface will produce valid _data_ for a record.
However, the _metadata_ is not interfaced. It is an open question how much we
should define these interfaces and avoid duplicating already existing
Marshmallow schemas.

At this point you might be wondering "Why not Marshmallow then?". The answer is
"separation of responsibilities, performance and simplicity". The later lays
with the fact that most of the data transformation is custom, so we would end
up with a schema full of `Method` fields, which does not differ much from what
we have but would have an impact on performance (Marshmallow is slow...).
Regarding the responsibilities part, validating - mostly referential, like
vocabularies - can only be done on _load_ where RDM instance knowledge/appctx
is available.

Note that no validation (not even structural) is done (at the moment) in this
step.

Load
----

The final step to have the records available in the RDM instance is to load
them. The available `load/postgresql:PostgreSQLCopyLoad` will carry out 2 steps:

- 1. Prepare the data, writing one DB row per line in a csv file:

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

A `TableGenerator` will, for each value in the received iterator, yield one
or more rows (lines to be written to the a csv file). For example for a record
it will yield: recid, DOI and OAI (PersistentIdentifiers), record and parent
metadata, etc.

Notes
=====

**Shared cache between streams**

During a migration run, there is a need to share information across different streams,
e.g populate communities before records and keep the map between community slug names
and autogenerated community ids, or at the same stream across different `TableGenerator`
instances, e.g on records stream we keep the "seen" parent ids so we can update the
information of the parent for different record versions.
For that reason, we pass a cache dict, that can change in the future in a type of
persistent storage e.g redis, in each `stream.load` step so streams can populate/consume
the cache.
The cache for each stream can also be populated in each stream configuration like below
in your `streams.yaml`:

.. code-block:: yaml

    records:
        extract:
            filename: /path/to/records.json
        load:
            cache:
                communities:
                    community_slug: <community_id>
            db_uri: postgresql+psycopg2://inveniordm:inveniordm@localhost:5432/inveniordm
            tmp_dir: /tmp/migrator

When the runner will instantiate each stream will merge the existing state of the cache
with whatever is provided in the stream configuration. That means, that the stream
configuration takes precedence and can override the whole cache before the stream runs!
Any cache state that exists before is overridden for the rest of the migration run.

**Infrastructure**

While now we are chaining the iterator from one step into the other in the
streams, the idea is that all three steps will pull/push to/from queues so
they can be deployed in different parts of the system (e.g. the load part
in the worker nodes).

**Others**

- Using generators instead of lists, allows us to iterate through the data
  only once and perform the E-T-L steps on them. Instead of loop for E, loop
  for T, loop for L. In addition, this allows us to have the csv files open
  during the writing and closing them at the end (open/close is an expensive
  op when done 3M times).
