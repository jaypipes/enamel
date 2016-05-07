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

import fixtures
from oslo_config import cfg

from enamel import opts


class ServiceFixture(fixtures.Fixture):
    """Run a service as a test fixture."""

    def __init__(self, cfg_section, app_entrypoint,
                 bind_address='0.0.0.0',
                 bind_port=0):
        self.app_entrypoint = app_entrypoint
        self.bind_port = bind_port
        self.bind_address = bind_address
        self._setup_conf()

    def _setup_conf(self):
        conf = cfg.ConfigOpts()
        conf = conf([], project=self.cfg_section)
        for group, options in opts.list_opts():
            conf.register_opts(list(options),
                               group=None if group == "DEFAULT" else group)
        conf.set_override('debug', True)
        conf.set_override('use_stderr', True)
        self.conf = conf

    def setUp(self):
        super(ServiceFixture, self).setUp()
        self.service = self.app_entrypoint(self.conf)
        self.service.run()
        self.addCleanup(self.service.stop)
