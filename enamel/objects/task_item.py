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

from oslo_versionedobjects import base as ovo_base
from oslo_versionedobjects import fields

from enamel.db import models as db_models
from enamel.db import utils as db_utils
from enamel.objects import base
from enamel.objects import exception as obj_exception


@ovo_base.VersionedObjectRegistry.register
class TaskItem(base.EnamelTimestampObject, base.EnamelObject):
    # Version 1.0: Initial version
    VERSION = '1.0'

    fields = {
        'id': fields.IntegerField(read_only=True),
        'uuid': fields.UUIDField(),
        'action': fields.StringField(),
        'state': fields.StringField(),
        'task_id': fields.IntegerField(),
        'ended_at': fields.DateTimeField(nullable=True),
    }

    @staticmethod
    def _from_db_object(task_item, db_task_item):
        for key in task_item.fields:
            setattr(task_item, key, db_task_item[key])
            task_item.obj_reset_changes()
        return task_item

    # TODO(alaski): Pass context through from middleware so oslo.db
    # EngineFacade work can be used.
    @staticmethod
    def _get_by_uuid_from_db(uuid):
        session = db_utils.get_session()
        db_task_item = session.query(db_models.TaskItem).filter_by(
                                                            uuid=uuid).first()

        if not db_task_item:
            raise obj_exception.TaskItemNotFound(uuid=uuid)

        return db_task_item

    @classmethod
    def get_by_uuid(cls, uuid):
        db_task_item = cls._get_by_uuid_from_db(uuid)
        return cls._from_db_object(cls(), db_task_item)

    @staticmethod
    def _create_in_db(updates):
        session = db_utils.get_session()
        db_task_item = db_models.TaskItem()
        db_task_item.update(updates)
        db_task_item.save(session)
        return db_task_item

    def create(self):
        db_task_item = self._create_in_db(self.obj_get_changes())
        self._from_db_object(self, db_task_item)
