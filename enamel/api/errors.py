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
