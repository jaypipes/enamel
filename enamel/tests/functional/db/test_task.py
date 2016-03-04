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


from oslo_utils import uuidutils

from enamel.objects import task
from enamel.tests import fixtures
from enamel.tests.unit import base as test_base


class TaskTestCase(test_base.DBTestCase):
    def setUp(self):
        super(TaskTestCase, self).setUp()
        self.useFixture(fixtures.Database())
        self._task_obj = task.Task()

    _sample_task = {
            'uuid': uuidutils.generate_uuid(),
            'action': 'boot_server',
            'state': 'in-progress',
            'request_id': 'req-foo',
            'user_id': 'foo',
            'project_id': 'bar',
            'params': '',
    }

    def _create_task(self):
        args = self._sample_task.copy()
        return self._task_obj._create_in_db(args)

    def test_get_by_uuid(self):
        task = self._create_task()
        db_task = self._task_obj._get_by_uuid_from_db(task['uuid'])
        for field in self._task_obj.fields.keys():
            self.assertEqual(task[field], db_task[field])
