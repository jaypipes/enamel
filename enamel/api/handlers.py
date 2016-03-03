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

# NOTE(cdent): We need a refactoring to break this into smaller
# modules soon.

import os
import re

import flask
import httpexceptor
from oslo_utils import uuidutils

from enamel.api import version


REQUEST_ID_HEADER = 'Openstack-Request-ID'


def handle_error(error):
    """Trap an HTTPException and package it for display"""
    # This current implementation is based on the httpexceptor model
    # which provides a very simple way to raise an HTTP<some status>
    # anywhere. This takes that exception, extracts meaning from it
    # and puts it in the format of an OpenStack errors object.

    status_code, title = error.status.split(' ', 1)
    # httpexcepter body() is a one item list of bytestring
    body_detail = error.body()[0].decode('utf-8')

    response = flask.jsonify({'errors': [{
        'status': int(status_code),
        'request_id': flask.g.request_id,
        'title': title,
        'detail': body_detail,
    }]})

    response.status = error.status
    for header, value in error.headers():
        if header.lower() == 'content-type':
            continue
        response.headers[header] = value
    return response


def handle_404(error):
    """Transform a Flask 404 into our error handling flow."""
    return handle_error(httpexceptor.HTTP404(error.description))


def set_request_id():
    """A before_request function to set required-id."""
    flask.g.request_id = uuidutils.generate_uuid()


def send_request_id(response):
    """An after_request_function to send request-id header."""
    response.headers[REQUEST_ID_HEADER] = flask.g.request_id
    return response


def set_version():
    """A before_request function to set microversion."""
    try:
        flask.g.request_version = version.extract_version(
            flask.request.headers)
    except ValueError as exc:
        flask.g.request_version = version.parse_version_string(
            version.min_version_string())
        raise httpexceptor.HTTP406('unable to use provided version: %s' % exc)


def send_version(response):
    """An after_request function to send microversion headers."""
    vary = response.headers.get('vary')
    header = version.Version.HEADER
    value = flask.g.get('request_version')
    if value:
        if vary:
            response.headers['vary'] = '%s, %s' % (vary, header)
        else:
            response.headers['vary'] = header
        response.headers[header] = '%s %s' % (version.SERVICE_TYPE, value)
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
