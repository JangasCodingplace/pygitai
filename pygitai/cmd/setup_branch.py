from datetime import datetime

from pygitai.common import config, get_logger
from pygitai.common.db_api import BranchInfoDBAPI, DoesNotExist
from pygitai.common.git import Git

logger = get_logger(__name__, config.logger.level)


def main(*args, **kwargs):
    current_branch = Git.get_current_branch()

    # check if there is a configuration already
    try:
        result = BranchInfoDBAPI.get(current_branch)
    except DoesNotExist:
        result = None

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
        BranchInfoDBAPI.update(current_branch, purpose, ticket_link)

    else:
        logger.info(f"Inserting row for {current_branch}")
        BranchInfoDBAPI.insert(current_branch, purpose, ticket_link, ts)
