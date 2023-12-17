import sqlite3
from dataclasses import dataclass

from .config import config


@dataclass
class BranchInfo:
    branch_name: str
    purpose: str
    ticket_link: str
    created_at: int


class DoesNotExist(Exception):
    pass


class BranchInfoDBAPI:
    @classmethod
    def create_table_if_not_exists(cls):
        with sqlite3.connect(config.general.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS branches (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    branch_name TEXT,
                    purpose TEXT,
                    ticket_link TEXT,
                    created_at INTEGER
                )
            """
            )
            connection.commit()

    @classmethod
    def insert(cls, branch_name: str, purpose: str, ticket_link: str, created_at: int):
        with sqlite3.connect(config.general.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO branches (branch_name, purpose, ticket_link, created_at)
                VALUES (?, ?, ?, ?)
            """,
                (branch_name, purpose, ticket_link, created_at),
            )
            connection.commit()

    @classmethod
    def update(cls, branch_name: str, purpose: str, ticket_link: str):
        with sqlite3.connect(config.general.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE branches
                SET
                    purpose = ?,
                    ticket_link = ?
                WHERE branch_name = ?
            """,
                (purpose, ticket_link, branch_name),
            )
            connection.commit()

    @classmethod
    def get(cls, branch_name: str) -> BranchInfo:
        with sqlite3.connect(config.general.db_name) as connection:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT * FROM branches WHERE branch_name = ?
            """,
                (branch_name,),
            )
            result = cursor.fetchone()
            if not result:
                raise DoesNotExist(f"Branch {branch_name} does not exist")
            return BranchInfo(
                branch_name=result[1],
                purpose=result[2],
                ticket_link=result[3],
                created_at=result[4],
            )
