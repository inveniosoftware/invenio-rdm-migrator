..
    Copyright (C) 2022 CERN.


    Invenio-RDM-Migrator is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======


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
