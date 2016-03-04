#!/usr/bin/env python
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
import httpexceptor
from keystonemiddleware import auth_token
from oslo_config import cfg
from oslo_log import log as logging

from enamel.api import handlers
from enamel import objects
from enamel import opts


LOG = logging.getLogger(__name__)


def create_app(conf):
    app = flask.Flask(__name__)
    _load_error_handlers(app)
    _load_request_handlers(app)
    _load_routes(app)
    # Here we work around keystone middleware's desire to be brought
    # into being via paste. Since we don't want to use paste we need
    # to tell the middleware that our keystone config is located in
    # a project with an oslo config.
    if conf.api.auth_strategy == 'keystone':
        auth_conf = {
            'log_name': __name__,
            'oslo_config_config': conf,
        }
        app.wsgi_app = auth_token.AuthProtocol(app.wsgi_app, auth_conf)
    return app


def prepare_service(args=None):
    if args is None:
        args = []
    conf = cfg.ConfigOpts()
    logging.register_options(conf)
    conf(args, project='enamel')
    logging.setup(conf, 'enamel')
    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == "DEFAULT" else group)

    return conf


def main(args=sys.argv[1:]):
    objects.register_all()
    conf = prepare_service(args)

    app = create_app(conf)
    app_kwargs = {'host': conf.api.bind_address,
                  'port': conf.api.bind_port}

    app.run(**app_kwargs)


def _load_error_handlers(app):
    app.error_handler_spec[None][None] = [(httpexceptor.HTTPException,
                                           handlers.handle_error)]
    # NOTE(cdent): A special handler is required for Flask's own 404,
    # it is likely one will be needed for at least 405 too.
    app.error_handler_spec[None][404] = handlers.handle_404


def _load_routes(app):
    # NOTE(cdent): Replace with package data map?
    # Use centralized declaration of routes to have non-global 'app'.
    app.add_url_rule('/', 'home', handlers.home, methods=['GET'])
    app.add_url_rule('/servers', 'server_boot', handlers.server_boot,
                     methods=['POST'])


def _load_request_handlers(app):
    # NOTE(cdent): This avoids the intrusion of 'app' into the
    # handlers module. Which may not actually matter. Depends on our
    # thoughts about all of flasks global hoopla.
    # We assume here that we are the first thing to mess with
    # before_request_funcs and after_request_funcs. This is true if
    # the before_request and after_request decorators are not used.
    app.before_request_funcs[None] = [
        handlers.set_request_id,  # keep this first
        handlers.set_version
    ]
    app.after_request_funcs[None] = [
        handlers.send_version,
        handlers.send_request_id
    ]


if __name__ == "__main__":
    sys.path.insert(0, '.')
    main()
