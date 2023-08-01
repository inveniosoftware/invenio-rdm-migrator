..
    Copyright (C) 2022 CERN.


    Invenio-RDM-Migrator is free software; you can redistribute it and/or
    modify it under the terms of the MIT License; see LICENSE file for more
    details.

Changes
=======


Version 2.0.0

- Make state globally available.
- Refactor transactions into actions. Create transaction and load data classes.
- Removed empty kafka extract module.
- Improved error handling and created specialized classes.
- Move `dict_set` to utils.
- Remove Python 3.8 from test matrix.

Version 1.0.0

- Initial public release.
