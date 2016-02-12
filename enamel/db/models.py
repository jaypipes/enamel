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

from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text


class ModelBase(models.ModelBase):
    __table_args__ = {'mysql_engine': 'InnoDB',
                      'mysql_charset': 'utf8'}

Base = declarative_base(cls=ModelBase)


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), nullable=False)
    action = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    request_id = Column(String(255), nullable=False)
    user_id = Column(String(255), nullable=False)
    project_id = Column(String(255), nullable=False)
    params = Column(Text, nullable=False)
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow,
            onupdate=timeutils.utcnow)
    ended_at = Column(DateTime)


class TaskItem(Base):
    __tablename__ = 'task_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), nullable=False)
    action = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    task_id = Column(Integer, ForeignKey('tasks.id'))
    created_at = Column(DateTime, default=timeutils.utcnow)
    updated_at = Column(DateTime, default=timeutils.utcnow,
            onupdate=timeutils.utcnow)
    ended_at = Column(DateTime)
