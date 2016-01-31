..
      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

===================
Database Migrations
===================

Running migrations
==================

Database migrations are handled under the hood by alembic so additional info on
commands can be found in the alembic documentation.

enamel-sync is added as a console script which sets up the proper environment
and then passes commands through to alembic. There is support for the
'upgrade', 'version', 'revision', and 'stamp' commands. The following arguments
are accepted for each command:

upgrade

.. option:: --revision <version>
    The migration number to upgrade to. 'head' can be specified to upgrade to
    that latest, and is the default if this argument is not passed.

revision

.. option:: -m <message>, --message <message>
    A short description of what the migration does.  This will be part of the
    migration name.
.. option:: --autogenerate
    Tells alembic it should attempt to generate the migration script based on
    updates to the defined models. Alembic docs provide good info on what
    changes can be detected for autogeneration. If this is not used a blank
    migration script will be created.

stamp

.. option:: --revision <version>
    Update the revision table in the database to this version. No migrations
    are run.

version: takes no arguments

The most common usages of enamel-sync are 'enamel-sync upgrade' to upgrade the
database and 'enamel-sync revision -m "change a thing" --autogenerate' to
generate a new migration.


Adding a migration
==================

The easiest way to add a migration is to update the database models in the
project and then run 'enamel-sync revision -m "short description"
--autogenerate'. This will add a new migration file configured to be run after
what was the HEAD migration at the time the command was run. Any updates beyond
simple column additions should be checked against the alembic documentation on
what can be autodetected. If necessary any further changes can be made directly
in the migration file generated.

There is a functional test suite that will verify that the database tables
after a migration match the database models that are defined. And there is a
test class 'WalkVersionsMixin' where further testing can be added for
individual migrations, for example if the integrity of existing data should be
checked.
