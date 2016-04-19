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
from enamel.objects import task_item
from enamel.tests import fixtures
from enamel.tests.unit import base as test_base


class TaskItemTestCase(test_base.DBTestCase):
    def setUp(self):
        super(TaskItemTestCase, self).setUp()
        self.useFixture(fixtures.Database())

    _sample_task = {
            'uuid': uuidutils.generate_uuid(),
            'action': 'boot_server',
            'state': 'in-progress',
            'request_id': 'req-foo',
            'user_id': 'foo',
            'project_id': 'bar',
            'params': '',
    }

    _sample_task_item = {
            'uuid': uuidutils.generate_uuid(),
            'action': 'create_volume',
            'state': 'in-progress',
            'task_id': None,
    }

    def _create_task_item(self):
        task_args = self._sample_task.copy()
        tsk = task.Task._create_in_db(task_args)
        task_item_args = self._sample_task_item.copy()
        task_item_args['task_id'] = tsk.id
        tsk_item = task_item.TaskItem._create_in_db(task_item_args)
        return tsk_item

    def test_get_by_uuid(self):
        tsk_item = self._create_task_item()
        db_task_item = task_item.TaskItem._get_by_uuid_from_db(
                tsk_item['uuid'])
        for field in task_item.TaskItem.fields.keys():
            self.assertEqual(tsk_item[field], db_task_item[field])
