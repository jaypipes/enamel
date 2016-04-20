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


from enamel import exception


class ObjectException(exception.EnamelException):
    msg_fmt = 'Error occurred with an object.'


class NotFound(ObjectException):
    msg_fmt = 'Object could not be found.'


class TaskNotFound(NotFound):
    msg_fmt = 'Task %(uuid)s could not be found.'


class TaskItemNotFound(NotFound):
    msg_fmt = 'TaskItem %(uuid)s could not be found.'
