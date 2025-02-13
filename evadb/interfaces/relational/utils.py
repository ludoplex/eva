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
import asyncio
from typing import Callable, List, Union

from evadb.binder.statement_binder import StatementBinder
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.database import EVADatabase
from evadb.executor.plan_executor import PlanExecutor
from evadb.expression.abstract_expression import AbstractExpression
from evadb.expression.constant_value_expression import ConstantValueExpression
from evadb.expression.tuple_value_expression import TupleValueExpression
from evadb.models.storage.batch import Batch
from evadb.optimizer.plan_generator import PlanGenerator
from evadb.optimizer.statement_to_opr_converter import StatementToPlanConverter
from evadb.parser.select_statement import SelectStatement
from evadb.parser.statement import AbstractStatement
from evadb.parser.table_ref import TableRef
from evadb.parser.utils import (
    parse_expression,
    parse_lateral_join,
    parse_predicate_expression,
)


def sql_string_to_expresssion_list(expr: str) -> List[AbstractExpression]:
    """Converts the sql expression to list of eva abstract expressions

    Args:
        expr (str): the expr to convert

    Returns:
        List[AbstractExpression]: list of eva abstract expressions

    """
    return parse_expression(expr)


def sql_predicate_to_expresssion_tree(expr: str) -> AbstractExpression:
    return parse_predicate_expression(expr)


def execute_statement(evadb: EVADatabase, statement: AbstractStatement) -> Batch:
    StatementBinder(StatementBinderContext(evadb.catalog)).bind(statement)
    l_plan = StatementToPlanConverter().visit(statement)
    p_plan = asyncio.run(PlanGenerator(evadb).build(l_plan))
    output = PlanExecutor(evadb, p_plan).execute_plan()
    if output:
        batch_list = list(output)
        return Batch.concat(batch_list, copy=False)


def string_to_lateral_join(expr: str, alias: str):
    return parse_lateral_join(expr, alias)


def create_star_expression():
    return [TupleValueExpression(col_name="*")]


def create_limit_expression(num: int):
    return ConstantValueExpression(num)


def try_binding(catalog: Callable, stmt: AbstractStatement):
    # To avoid complications in subsequent binder calls, we attempt to bind a copy of
    # the statement since the binder modifies the statement in place and can cause
    # issues if statement is partially bound.
    StatementBinder(StatementBinderContext(catalog)).bind(stmt.copy())


def handle_select_clause(
    query: SelectStatement, alias: str, clause: str, value: Union[str, int, list]
) -> SelectStatement:
    """
    Modifies a SELECT statement object by adding or modifying a specific clause.

    Args:
        query (SelectStatement): The SELECT statement object.
        alias (str): Alias for the table reference.
        clause (str): The clause to be handled.
        value (str, int, list): The value to be set for the clause.

    Returns:
        SelectStatement: The modified SELECT statement object.

    Raises:
        AssertionError: If the query is not an instance of SelectStatement class.
        AssertionError: If the clause is not in the accepted clauses list.
    """

    assert isinstance(
        query, SelectStatement
    ), "query must be an instance of SelectStatement"

    accepted_clauses = [
        "where_clause",
        "target_list",
        "groupby_clause",
        "orderby_list",
        "limit_count",
    ]

    assert clause in accepted_clauses, f"Unknown clause: {clause}"

    # If the clause being set is "target_list" and the value is equal to
    # "*", the "SELECT *" portion is replaced by SELECT <value>.
    if clause == "target_list" and getattr(query, clause) == create_star_expression():
        setattr(query, clause, None)

    if getattr(query, clause) is None:
        setattr(query, clause, value)
    else:
        query = SelectStatement(
            target_list=create_star_expression(),
            from_table=TableRef(query, alias=alias),
        )
        setattr(query, clause, value)

    return query
