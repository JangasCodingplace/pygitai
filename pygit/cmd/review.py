from pygit.common.git import Git

from .commit import process_user_feedback_llm_loop


def main(
    target_branch: str,
    *args,
    **kwargs,
):
    current_branch = Git.get_current_branch()
    diff = Git.get_diff_between_branches(
        branch_1=target_branch,
        branch_2=current_branch,
    )
    process_user_feedback_llm_loop(
        context="feedback_on_commit",
        context_user={"diff": diff},
    )
