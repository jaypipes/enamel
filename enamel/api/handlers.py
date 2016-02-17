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

import flask

from enamel.api import version


def set_version():
    """A before_request function to set microversion."""
    try:
        flask.g.request_version = version.extract_version(
            flask.request.headers)
    except ValueError:  # as exc:
        # TODO(cdent): raise a proper 406
        raise


def send_version(response):
    """An after_request function to send microversion headers."""
    vary = response.headers.get('vary')
    header = version.Version.HEADER
    value = flask.g.request_version
    if vary:
        response.headers['vary'] = '%s, %s' % (vary, header)
    else:
        response.headers['vary'] = header
    response.headers[header] = value
    return response


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
