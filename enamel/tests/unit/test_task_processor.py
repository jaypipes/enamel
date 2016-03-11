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

from enamel import task_processor
from enamel.tests.unit import base


class TestTaskProcessor(base.TestCase):
    def test_is_running(self):
        p = task_processor.TaskProcessor()
        self.assertFalse(p.is_running())
        p.run()
        self.assertTrue(p.is_running())
