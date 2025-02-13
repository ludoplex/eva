# coding=utf-8
# Copyright 2018-2023 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound

from evadb.catalog.models.base_model import BaseModel


class BaseService:
    """
    Base service for all the models. Implemented by all other services.
    The services perform business logic using the model provided
    """

    def __init__(self, model: BaseModel, session: Session):
        self.model = model
        self.session = session
        self.query = session.query(model)

    def get_all_entries(self) -> List:
        try:
            entries = self.query.all()
            return [entry.as_dataclass() for entry in entries]
        except NoResultFound:
            return []
