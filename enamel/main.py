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

import os
import re
import sys

import flask
from oslo_config import cfg

from enamel import opts


def create_app():
    app = flask.Flask(__name__)
    # Use centralized declaration of routes to have non-global
    # 'app'.
    _load_routes(app)
    return app


def create_link_object(urls):
    links = []
    for url in urls:
        links.append({"rel": "self",
                      "href": os.path.join(flask.request.url_root, url)})
    return links


def generate_resource_data(resources):
    data = []
    for resource in resources:
        item = {}
        item['name'] = str(resource).split('/')[-1]
        item['links'] = create_link_object([str(resource)[1:]])
        data.append(item)
    return data


def home():
    pat = re.compile("^\/[^\/]*?$")

    resources = []
    for url in flask.current_app.url_map.iter_rules():
        if pat.match(str(url)):
            resources.append(url)

    return flask.jsonify(resources=generate_resource_data(resources))


def server_boot():
    data = flask.request.get_json()
    # TODO(cdent): Call the task workflow here and return a link to the task
    task_return = data
    return flask.jsonify(task_return)


def main(args=sys.argv[1:]):
    conf = cfg.ConfigOpts()
    conf(args, project='enamel')
    for group, options in opts.list_opts():
        conf.register_opts(list(options),
                           group=None if group == "DEFAULT" else group)

    app = create_app()
    app_kwargs = {'host': conf.api.bind_address,
                  'port': conf.api.bind_port}

    app.run(**app_kwargs)


def _load_routes(app):
    # NOTE(cdent): Replace with package data map?
    app.add_url_rule('/', 'home', home, methods=['GET'])
    app.add_url_rule('/servers', 'server_boot', server_boot, methods=['POST'])
