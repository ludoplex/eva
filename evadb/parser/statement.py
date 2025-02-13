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
from copy import deepcopy

from evadb.parser.types import StatementType


class AbstractStatement:
    """
    Base class for all Statements

    Attributes
    ----------
    stmt_type : StatementType
        the type of this statement - Select or Insert etc
    """

    def __init__(self, stmt_type: StatementType):
        self._stmt_type = stmt_type

    @property
    def stmt_type(self):
        return self._stmt_type

    def __hash__(self) -> int:
        return hash(self.stmt_type)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result

    def copy(self):
        """Returns a deepcopy of the statement."""
        return deepcopy(self)
