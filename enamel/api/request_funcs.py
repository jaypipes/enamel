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

import flask
import httpexceptor
from oslo_utils import uuidutils

from enamel.api import version


REQUEST_ID_HEADER = 'Openstack-Request-ID'


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
