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

import functools

import flask
import httpexceptor


ACCEPTABLE_TYPES = ['application/json', 'application/vnd.enamel+json']


def accept(types=ACCEPTABLE_TYPES):
    """Decorate a route to only accept given types.

    Note that this makes no account for quality statements within accept
    headers. In the current environment this is satisfactory as we are
    not providing different serializations of resources.
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            acceptable = flask.request.accept_mimetypes.values()
            if not set.intersection(set(acceptable), set(types)):
                raise httpexceptor.HTTP406('Need %s' % types)
            else:
                return f(*args, **kwargs)
        return decorated_function
    return decorator
