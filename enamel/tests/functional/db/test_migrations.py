#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Tests for database migrations.
There are "opportunistic" tests which allows testing against all 3 databases
(sqlite in memory, mysql, pg) in a properly configured unit test environment.

For the opportunistic testing you need to set up db's named 'openstack_citest'
with user 'openstack_citest' and password 'openstack_citest' on localhost. The
test will then use that db and u/p combo to run the tests.

For postgres on Ubuntu this can be done with the following commands::

| sudo -u postgres psql
| postgres=# create user openstack_citest with createdb login password
|       'openstack_citest';
| postgres=# create database openstack_citest with owner openstack_citest;

"""

import contextlib
import mock

from alembic import script
from oslo_db.sqlalchemy import test_base
from oslo_db.sqlalchemy import test_migrations
from oslo_db.sqlalchemy import utils as sql_utils
from oslo_log import log as logging

from enamel.db import models
from enamel.db import sync
from enamel.db import utils as db_utils

LOG = logging.getLogger(__name__)


@contextlib.contextmanager
def patch_with_engine(engine):
    with mock.patch.object(db_utils, 'get_engine') as patch_engine:
        patch_engine.return_value = engine
        yield


class ModelsSyncMixin(test_migrations.ModelsMigrationsSync):
    """Test that the models match the database after migrations are run."""

    def db_sync(self, engine):
        with patch_with_engine(engine):
            alemb_conf = sync.get_alembic_config()
            sync.do_alembic_command(alemb_conf, 'upgrade', revision='head')

    @property
    def migrate_engine(self):
        return self.engine

    def get_engine(self):
        return self.migrate_engine

    def get_metadata(self):
        return models.Base.metadata


class ModelsMigrationsSyncSQLite(ModelsSyncMixin,
                                 test_migrations.ModelsMigrationsSync,
                                 test_base.DbTestCase):
    pass


class ModelsMigrationsSyncMysql(ModelsSyncMixin,
                                test_migrations.ModelsMigrationsSync,
                                test_base.MySQLOpportunisticTestCase):
    pass


class ModelsMigrationsSyncPostgres(ModelsSyncMixin,
                                   test_migrations.ModelsMigrationsSync,
                                   test_base.PostgreSQLOpportunisticTestCase):
    pass


class WalkVersionsMixin(object):
    def test_walk_versions(self):
        # Determine latest version script from the repo, then
        # upgrade from 1 through to the latest, with no data
        # in the databases. This just checks that the schema itself
        # upgrades successfully.

        alembic_cfg = sync.get_alembic_config()

        # Place the database under version control
        with patch_with_engine(self.engine):

            script_directory = script.ScriptDirectory.from_config(alembic_cfg)

            self.assertIsNone(sync._version(alembic_cfg))

            versions = [ver for ver in script_directory.walk_revisions()]

            for version in reversed(versions):
                self._migrate_up(self.engine, alembic_cfg, version.revision)

    def _migrate_up(self, engine, config, version, with_data=False):
        """migrate up to a new version of the db.

        We allow for data insertion and post checks at every
        migration version with special _pre_upgrade_### and
        _check_### functions in the main test.
        """
        # NOTE(sdague): try block is here because it's impossible to debug
        # where a failed data migration happens otherwise
        try:
            data = None
            pre_upgrade = getattr(
                self, "_pre_upgrade_%s" % version, None)
            if pre_upgrade:
                data = pre_upgrade(engine)

            sync.do_alembic_command(config, 'upgrade', version)
            self.assertEqual(version, sync._version(config))
            check = getattr(self, "_check_%s" % version, None)
            if check:
                check(engine, data)
        except Exception:
            LOG.error("Failed to migrate to version %(version)s on engine "
                      "%(engine)s", {'version': version, 'engine': engine})
            raise

    def _check_ee6d6ae007c1(self, engine, data):
        # NOTE(alaski): This is an example check.  For this migration the
        # models sync check tests everything needed.
        tasks_table = sql_utils.get_table(engine, 'tasks')
        self.assertIsNotNone(tasks_table)
        task_items_table = sql_utils.get_table(engine, 'task_items')
        self.assertIsNotNone(task_items_table)


class TestMigrationsSQLite(WalkVersionsMixin,
                           test_base.DbTestCase):
    pass


class TestMigrationsMySQL(WalkVersionsMixin,
                          test_base.MySQLOpportunisticTestCase):
    pass


class TestMigrationsPostgreSQL(WalkVersionsMixin,
                               test_base.PostgreSQLOpportunisticTestCase):
    pass
