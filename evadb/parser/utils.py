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
from evadb.parser.create_udf_statement import CreateUDFStatement
from evadb.parser.drop_statement import DropTableStatement
from evadb.parser.drop_udf_statement import DropUDFStatement
from evadb.parser.load_statement import LoadDataStatement
from evadb.parser.parser import Parser
from evadb.parser.select_statement import SelectStatement


def parse_expression(expr: str):
    mock_query = f"SELECT {expr} FROM DUMMY;"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.target_list


def parse_predicate_expression(expr: str):
    mock_query = f"SELECT * FROM DUMMY WHERE {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.where_clause


def parse_table_clause(expr: str):
    mock_query = f"SELECT * FROM {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert stmt.from_table.is_table_atom
    return stmt.from_table


def parse_create_udf(
    udf_name: str, if_not_exists: bool, udf_file_path: str, type: str, **kwargs
):
    mock_query = (
        f"CREATE UDF IF NOT EXISTS {udf_name}"
        if if_not_exists
        else f"CREATE UDF {udf_name}"
    )
    if type is not None:
        mock_query += f" TYPE {type}"
        task, model = kwargs["task"], kwargs["model"]
        if task is not None and model is not None:
            mock_query += f" 'task' '{task}' 'model' '{model}'"
    else:
        mock_query += f" IMPL '{udf_file_path}'"
    mock_query += ";"

    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, CreateUDFStatement), "Expected a create udf statement"
    return stmt


def parse_load(table_name: str, file_regex: str, format: str, **kwargs):
    mock_query = f"LOAD {format.upper()} '{file_regex}' INTO {table_name};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, LoadDataStatement), "Expected a load statement"
    return stmt


def parse_drop(table_name: str, if_exists: bool, **kwargs):
    mock_query = (
        f"DROP TABLE IF EXISTS {table_name}"
        if if_exists
        else f"DROP TABLE {table_name}"
    )
    mock_query += ";"

    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, DropTableStatement), "Expected a drop table statement"
    return stmt


def parse_drop_udf(udf_name: str, if_exists: bool, **kwargs):
    mock_query = (
        f"DROP UDF IF EXISTS {udf_name}" if if_exists else f"DROP UDF {udf_name}"
    )
    mock_query += ";"

    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, DropUDFStatement), "Expected a drop udf statement"
    return stmt


def parse_query(query):
    stmt = Parser().parse(query)
    assert len(stmt) == 1
    return stmt[0]


def parse_lateral_join(expr: str, alias: str):
    mock_query = f"SELECT * FROM DUMMY JOIN LATERAL {expr} AS {alias};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert stmt.from_table.is_join()
    return stmt.from_table.join_node.right


def parse_create_vector_index(index_name: str, table_name: str, expr: str, using: str):
    mock_query = f"CREATE INDEX {index_name} ON {table_name} ({expr}) USING {using};"
    return Parser().parse(mock_query)[0]


def parse_sql_orderby_expr(expr: str):
    mock_query = f"SELECT * FROM DUMMY ORDER BY {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.orderby_list
