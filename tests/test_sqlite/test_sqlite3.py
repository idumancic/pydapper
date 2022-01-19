import datetime
import sqlite3
from dataclasses import dataclass

from pydapper import connect
from pydapper import using
from pydapper.sqlite import Sqlite3Commands


class TestExecute:
    def test_single(self, sqlite3_connection):
        assert (
            sqlite3_connection.execute(
                "UPDATE owner SET name = ?new_name? WHERE id = ?id?", {"new_name": "Zachary", "id": "1"}
            )
            == 1
        )

    def test_multiple(self, sqlite3_connection):
        assert (
            sqlite3_connection.execute(
                "INSERT INTO task (description, due_date, owner_id) VALUES (?description?, ?due_date?, ?owner_id?)",
                [
                    {"description": "new task", "due_date": "2022-01-01", "owner_id": 1},
                    {"description": "another new task", "due_date": "2022-01-01", "owner_id": 1},
                ],
            )
            == 2
        )


class TestQuery:
    def test(self, sqlite3_connection):
        data = sqlite3_connection.query("select * from task")
        assert len(data) == 3
        assert all(isinstance(record, dict) for record in data)

    def test_param(self, sqlite3_connection):
        data = sqlite3_connection.query(
            "select * from task where due_date = ?due_date?", param={"due_date": "2021-12-31"}
        )
        assert len(data) == 2
        assert all(isinstance(record, dict) for record in data)


class TestQueryMultiple:
    def test(self, sqlite3_connection):
        owner, task = sqlite3_connection.query_multiple(("select * from owner", "select * from task"))
        assert len(owner) == 1
        assert len(task) == 3
        assert isinstance(owner[0], dict)
        assert all(isinstance(record, dict) for record in task)

    def test_param(self, sqlite3_connection):
        owner, task = sqlite3_connection.query_multiple(
            ("select * from owner where id = ?id?", "select * from task where due_date = ?due_date?"),
            param={"id": 1, "due_date": "2021-12-31"},
        )
        assert len(owner) == 1
        assert len(task) == 2
        assert isinstance(owner[0], dict)
        assert all(isinstance(record, dict) for record in task)

    def test_different_models(self, sqlite3_connection):
        @dataclass
        class Task:
            id: int
            description: str
            due_date: datetime.date
            owner_id: int

        @dataclass
        class Owner:
            id: int
            name: str

        owner, task = sqlite3_connection.query_multiple(
            ("select * from owner", "select * from task"), models=(Owner, Task)
        )

        assert len(owner) == 1
        assert len(task) == 3
        assert isinstance(owner[0], Owner)
        assert all(isinstance(record, Task) for record in task)


class TestQueryFirst:
    def test(self, sqlite3_connection):
        task = sqlite3_connection.query_first("select * from task")
        assert isinstance(task, dict)

    def test_param(self, sqlite3_connection):
        task = sqlite3_connection.query_first("select * from task where id = ?id?", param={"id": 1})
        assert task["id"] == 1


class TestQueryFirstOrDefault:
    def test(self, sqlite3_connection):
        sentinel = object()
        task = sqlite3_connection.query_first_or_default("select * from task where id = 1000", default=sentinel)
        assert task is sentinel

    def test_param(self, sqlite3_connection):
        sentinel = object()
        task = sqlite3_connection.query_first_or_default(
            "select * from task where id = ?id?", param={"id": 1000}, default=sentinel
        )
        assert task is sentinel


class TestQuerySingle:
    def test(self, sqlite3_connection):
        task = sqlite3_connection.query_single("select * from task where id = 1")
        assert task["id"] == 1

    def test_param(self, sqlite3_connection):
        task = sqlite3_connection.query_single("select * from task where id = ?id?", param={"id": 1})
        assert task["id"] == 1


class TestQuerySingleOrDefault:
    def test(self, sqlite3_connection):
        sentinel = object()
        task = sqlite3_connection.query_single_or_default("select * from task where id = 1000", default=sentinel)
        assert task is sentinel

    def test_param(self, sqlite3_connection):
        sentinel = object()
        task = sqlite3_connection.query_single_or_default(
            "select * from task where id = ?id?", param={"id": 1000}, default=sentinel
        )
        assert task is sentinel


class TestExecuteScalar:
    def test(self, sqlite3_connection):
        owner_name = sqlite3_connection.execute_scalar("select name from owner")
        assert owner_name == "Zach Schumacher"

    def test_param(self, sqlite3_connection):
        first_task_description = sqlite3_connection.execute_scalar(
            "select description from task where id = ?id?", param={"id": 1}
        )
        assert first_task_description == "Set up a test database"


def test_using(database_name):
    with using(sqlite3.connect(f"{database_name}.db")) as commands:
        assert isinstance(commands, Sqlite3Commands)


def test_connect(application_dsn):
    with connect(application_dsn) as commands:
        assert isinstance(commands, Sqlite3Commands)
