..
    Copyright (C) 2022-2023 CERN.


    Invenio-RDM-Migrator is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======

Version 4.4.1

- Fix default value for nullable model fields.

Version 4.4.0

- Add GitHub stream.
- Add ``verified_at`` and ``blocked_at`` for usesr models.
- Handle parent DOIs for records.
- Add media files to records and drafts.
- Add ``deletion_status`` to record models.
- Switch to ``orjson`` for JSON dumping/loading.
- Add multi-processing for transform.
- Refactor state to also use Python dict for caching.

Version 4.3.0

- Add community basic CRUD actions.
- Add DB session fixtures.

Version 4.2.0

- Rename `FileUploadAction` to `DraftFileUploadAction`.

Version 4.1.0

- Add file upload action.
- Add draft edit action.

Version 4.0.0

- Namespace actions by load and transform.

Version 3.1.0

- Add `DatetimeMixin` to transform timestamps into iso formatted date strings.
- Add `JSONLoadMixin` to load dictionaries from strings.

Version 3.0.0

- `Operation` instances have split the model and the data into two attributes.
- Add user actions.
- `PostgreSQLTx` `resolve_references` function has now a default behaviour (`pass`).
- Add nullable configuration to draft and user related models.
- Minor bug fixes.

Version 2.0.0

- Make state globally available.
- Refactor transactions into actions. Create transaction and load data classes.
- Removed empty kafka extract module.
- Improved error handling and created specialized classes.
- Move `dict_set` to utils.
- Remove Python 3.8 from test matrix.

Version 1.0.0

- Initial public release.
