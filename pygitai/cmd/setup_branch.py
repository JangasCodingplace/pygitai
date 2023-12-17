import sqlite3
from datetime import datetime

from pygitai.common import config, get_logger
from pygitai.common.git import Git

logger = get_logger(__name__, config.logger.level)


def main(*args, **kwargs):
    current_branch = Git.get_current_branch()

    with sqlite3.connect(config.general.db_name) as connection:
        cursor = connection.cursor()

        # check if there is a configuration already
        cursor.execute(f"SELECT * FROM branches WHERE branch_name = '{current_branch}'")
        result = cursor.fetchone()
        if result:
            logger.warning(f"Branch {current_branch} already has a configuration")

        purpose_input_text = (
            "[Optional] Enter the purpose of the branch "
            f"(current branch is {current_branch}): "
        )
        if result:
            purpose_input_text = (
                "[Optional] Enter the purpose of the branch "
                f"(current purpose is {result[2]}): "
            )
        else:
            purpose_input_text = (
                "[Optional] Enter the purpose of the branch "
                f"(current branch is {current_branch}): "
            )
        purpose = input(purpose_input_text)
        if result:
            purpose = purpose or result[2]

        if result:
            ticket_link_input_text = (
                "[Optional] Enter the ticket link "
                f"(current ticket link is {result[3]}): "
            )
        else:
            ticket_link_input_text = (
                "[Optional] Enter the ticket link "
                f"(current branch is {current_branch}): "
            )
        ticket_link = input(ticket_link_input_text)
        if result:
            ticket_link = ticket_link or result[3]

        if result:
            ts = result[4]
        else:
            ts = datetime.now().timestamp()

        if result:
            logger.info(f"Updating row fpr {current_branch}")
            cursor.execute(
                """
                UPDATE branches
                SET
                    purpose = ?,
                    ticket_link = ?
                WHERE branch_name = ?
            """,
                (purpose, ticket_link, current_branch),
            )
        else:
            logger.info(f"Inserting row for {current_branch}")
            cursor.execute(
                f"""
                INSERT INTO branches (branch_name, purpose, ticket_link, created_at)
                VALUES ('{current_branch}', '{purpose}', '{ticket_link}', {int(ts)})
            """
            )
        connection.commit()
