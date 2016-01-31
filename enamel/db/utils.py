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

from oslo_db.sqlalchemy import session

_FACADE = None


def init(conf):
    global _FACADE
    _FACADE = session.EngineFacade.from_config(conf)


def get_session(**kwargs):
    return _FACADE.get_session(**kwargs)


def get_engine():
    return _FACADE.get_engine()
