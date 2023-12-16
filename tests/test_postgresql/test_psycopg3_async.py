import datetime

import pytest
import pytest_asyncio

from pydapper import connect_async
from pydapper import using_async
from pydapper.commands import CommandsAsync
from pydapper.postgresql.psycopg3 import Psycopg3CommandsAsync
from tests.test_suites.commands import ExecuteAsyncTestSuite
from tests.test_suites.commands import ExecuteScalarAsyncTestSuite
from tests.test_suites.commands import QueryAsyncTestSuite
from tests.test_suites.commands import QueryFirstAsyncTestSuite
from tests.test_suites.commands import QueryFirstOrDefaultAsyncTestSuite
from tests.test_suites.commands import QueryMultipleAsyncTestSuite
from tests.test_suites.commands import QuerySingleAsyncTestSuite
from tests.test_suites.commands import QuerySingleOrDefaultAsyncTestSuite

pytestmark = pytest.mark.postgresql


@pytest_asyncio.fixture(scope="function")
async def commands(server, database_name) -> Psycopg3CommandsAsync:
    import psycopg

    conn = await psycopg.AsyncConnection.connect(f"postgresql://pydapper:pydapper@{server}:5433/{database_name}")
    async with Psycopg3CommandsAsync(conn) as commands:
        yield commands
        await commands.connection.rollback()


@pytest.mark.asyncio
async def test_using_async(server, database_name):
    import psycopg

    conn = await psycopg.AsyncConnection.connect(f"postgresql://pydapper:pydapper@{server}:5433/{database_name}")
    async with using_async(conn) as commands:
        assert isinstance(commands, Psycopg3CommandsAsync)


@pytest.mark.asyncio
async def test_connect_async(server, database_name):
    async with connect_async(f"postgresql+psycopg://pydapper:pydapper@{server}:5433/{database_name}") as commands:
        assert isinstance(commands, Psycopg3CommandsAsync)


class TestExecute(ExecuteAsyncTestSuite):
    @pytest.mark.asyncio
    async def test_multiple(self, commands: CommandsAsync):
        assert (
            await commands.execute_async(
                "INSERT INTO task (id, description, due_date, owner_id) "
                "VALUES (?id?, ?description?, ?due_date?, ?owner_id?)",
                [
                    {"id": 4, "description": "new task", "due_date": datetime.date(2022, 1, 1), "owner_id": 1},
                    {"id": 5, "description": "another new task", "due_date": datetime.date(2022, 1, 1), "owner_id": 1},
                ],
            )
            == 2
        )


class TestQueryAsync(QueryAsyncTestSuite):
    ...


class TestQueryMultipleAsync(QueryMultipleAsyncTestSuite):
    ...


class TestQueryFirstAsync(QueryFirstAsyncTestSuite):
    ...


class TestQueryFirstOrDefaultAsync(QueryFirstOrDefaultAsyncTestSuite):
    ...


class TestQuerySingleAsync(QuerySingleAsyncTestSuite):
    ...


class TestQuerySingleOrDefaultAsync(QuerySingleOrDefaultAsyncTestSuite):
    ...


class TestExecuteScalarAsync(ExecuteScalarAsyncTestSuite):
    ...