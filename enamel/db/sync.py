# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os
import sys

from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import migration as alembic_migration
from alembic import util as alembic_util
import six
from oslo_config import cfg
from oslo_db import options as db_options

from enamel.db import utils as db_utils
from enamel import opts


def _upgrade(conf):
    revision = conf.enamel_config.command.revision or 'head'
    do_alembic_command(conf, 'upgrade', revision=revision)


def _version(conf):
    engine = db_utils.get_engine()
    with engine.connect() as conn:
        context = alembic_migration.MigrationContext.configure(conn)
        return context.get_current_revision()


def _revision(conf):
    return do_alembic_command(conf, 'revision',
            message=conf.enamel_config.command.message,
            autogenerate=conf.enamel_config.command.autogenerate)


def _stamp(conf):
    return do_alembic_command(conf, 'stamp',
            revision=conf.enamel_config.command.revision)


def do_alembic_command(config, cmd, *args, **kwargs):
    try:
        getattr(alembic_command, cmd)(config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(six.text_type(e))


def get_alembic_config():
    return alembic_config.Config(os.path.join(os.path.dirname(__file__),
        'alembic.ini'))


def add_command_parsers(subparsers):
    parser = subparsers.add_parser(
        'upgrade',
        help="Upgrade the database schema to the latest version. "
             "Optionally, use --revision to specify an alembic revision "
             "string to upgrade to.")
    parser.set_defaults(func=_upgrade)
    parser.add_argument('--revision', nargs='?')

    parser = subparsers.add_parser('stamp')
    parser.add_argument('--revision', nargs='?')
    parser.set_defaults(func=_stamp)

    parser = subparsers.add_parser(
        'revision',
        help="Create a new alembic revision. "
             "Use --message to set the message string.")
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')
    parser.set_defaults(func=_revision)

    parser = subparsers.add_parser(
        'version',
        help="Print the current version information and exit.")
    parser.set_defaults(func=_version)


command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help='Available commands',
                                handler=add_command_parsers)


def main(args=sys.argv[1:]):
    conf = cfg.ConfigOpts()
    conf.register_cli_opt(command_opt)
    db_options.set_defaults(conf)
    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == 'Default' else group)
    conf(args, project='enamel')
    db_utils.init(conf)
    al_conf = get_alembic_config()
    al_conf.enamel_config = conf

    conf.command.func(al_conf)
