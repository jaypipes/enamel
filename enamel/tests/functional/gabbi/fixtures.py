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

from gabbi import fixture
from keystonemiddleware import auth_token

from enamel import main


# NOTE(cdent): Workaround difficulties using config as a fixture.
# We want to use a different WSGI application and config per each
# test file, but there is no easy way to reach into the app factory
# except by allowing it (setup_app) to be closed over a CONF that we
# manage from the fixture.
CONF = None


def setup_app():
    global CONF
    return main.create_app(CONF)


class BaseConfigFixture(fixture.GabbiFixture):
    """Use a different olso config for each test suite."""

    def __init__(self):
        self.conf = None

    def start_fixture(self):
        self._manage_conf()
        self.override_config()

    def override_config(self):
        self.conf.set_override('debug', True)
        self.conf.set_override('use_stderr', True)

    def _manage_conf(self):
        global CONF
        conf = main.prepare_service()
        CONF = self.conf = conf

    def stop_fixture(self):
        self.conf.reset()


class ConfigFixture(BaseConfigFixture):

    def override_config(self):
        """Turn off keystone."""
        super(ConfigFixture, self).override_config()
        self.conf.set_override('auth_strategy', None, 'api')


class AuthedConfigFixture(BaseConfigFixture):
    """Run tests with keystone middleware in place.

    For the time being this means: make a test sprout a 401.
    """

    def override_config(self):
        """Allow keystone to run, and set defaults."""
        super(AuthedConfigFixture, self).override_config()
        self.conf.register_opts(auth_token._OPTS, group='keystone_authtoken')
        self.conf.set_override('auth_uri', 'http://127.0.0.1:35357',
                               group='keystone_authtoken')
