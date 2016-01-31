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

import sys

import flask
from keystonemiddleware import auth_token
from oslo_config import cfg

from enamel.api import handlers
from enamel import opts


def create_app(conf):
    app = flask.Flask(__name__)
    _load_routes(app)
    # Here we work around keystone middleware's desire to be brought
    # into being via paste. Since we don't want to use paste we need
    # to tell the middleware that our keystone config is located in
    # a project with an oslo config.
    if conf.api.auth_strategy == 'keystone':
        keystone_middleware = auth_token.filter_factory(
            {}, oslo_config_project='enamel')
        app.wsgi_app = keystone_middleware(app.wsgi_app)
    return app


def main(args=sys.argv[1:]):
    conf = cfg.ConfigOpts()
    conf(args, project='enamel')
    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == "DEFAULT" else group)

    app = create_app(conf)

    app_kwargs = {'host': conf.api.bind_address,
                  'port': conf.api.bind_port}

    app.run(**app_kwargs)


def _load_routes(app):
    # NOTE(cdent): Replace with package data map?
    # Use centralized declaration of routes to have non-global 'app'.
    app.add_url_rule('/', 'home', handlers.home, methods=['GET'])
    app.add_url_rule('/servers', 'server_boot', handlers.server_boot,
                     methods=['POST'])
