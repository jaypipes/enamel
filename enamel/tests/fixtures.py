# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Without this 'import fixtures' actually imports enamel.tests.fixtures
from __future__ import absolute_import

import fixtures

from enamel.db import sync as db_sync
from enamel.db import utils as db_utils

DB_SCHEMA = ''


class Database(fixtures.Fixture):
    def __init__(self):
        super(Database, self).__init__()
        self.get_engine = db_utils.get_engine

    def setUp(self):
        super(Database, self).setUp()
        self.reset()
        self.addCleanup(self.cleanup)

    def _cache_schema(self):
        global DB_SCHEMA
        if not DB_SCHEMA:
            engine = self.get_engine()
            conn = engine.connect()
            alemb_conf = db_sync.get_alembic_config()
            db_sync.do_alembic_command(alemb_conf, 'upgrade', revision='head')
            DB_SCHEMA = "".join(line for line in conn.connection.iterdump())

    def cleanup(self):
        engine = self.get_engine()
        engine.dispose()

    def reset(self):
        self._cache_schema()
        engine = self.get_engine()
        engine.dispose()
        conn = engine.connect()
        conn.connection.executescript(DB_SCHEMA)
