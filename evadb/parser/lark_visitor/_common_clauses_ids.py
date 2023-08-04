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

from evadb.catalog.catalog_type import Dimension
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.parser.table_ref import TableInfo
from evadb.utils.logging_manager import logger


class CommonClauses:
    def table_name(self, tree):
        table_name = self.visit(tree.children[0])
        if table_name is not None:
            return TableInfo(table_name=table_name)
        error = "Invalid Table Name"
        logger.error(error)

    def full_id(self, tree):
        return self.visit(tree.children[0])

    def uid(self, tree):
        return self.visit(tree.children[0])

    def full_column_name(self, tree):
        uid = self.visit(tree.children[0])

        # check for dottedid
        if len(tree.children) > 1:
            dotted_id = self.visit(tree.children[1])
            return TupleValueExpression(table_alias=uid, col_name=dotted_id)
        else:
            return TupleValueExpression(col_name=uid)

    def dotted_id(self, tree):
        dotted_id = str(tree.children[0])
        return dotted_id.lstrip(".")

    def simple_id(self, tree):
        return str(tree.children[0])

    def decimal_literal(self, tree):
        decimal = None
        token = tree.children[0]
        return Dimension.ANYDIM if str.upper(token) == "ANYDIM" else int(str(token))

    def real_literal(self, tree):
        return float(tree.children[0])
