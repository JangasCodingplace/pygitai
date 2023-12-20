import json

from pygitai.common.config import config
from pygitai.common.db_api import BranchInfoDBAPI, DoesNotExist
from pygitai.common.git import Git
from pygitai.common.git import PreCommitHook as GitPreCommitHook
from pygitai.common.git import state as git_state

from .base_job import BaseJob
from .llm_job import LLMJobBase


class AutoStageAll(BaseJob):
    """Auto stage all not staged files

    This is not a LLM job.
    It's a Git Job.
    """

    cli_configurable_name = "auto_stage_all"

    def exec_command(self, *args, **kwargs):
        Git.exec_stage_files(["-A"])


class PreCommitHook(BaseJob):
    """If Pre-commit hook are used, run them without commiting.

    This is typically used to run before a LLM Commit Job for saving
    costs.

    No Environment variables has to be set for this to work.
    This job autoamtically detects if pre-commit hooks are used.

    This is not a LLM job.
    It's a Git Job.
    """

    def exec_command(self, *args, **kwargs):
        if config.git.pre_commit:
            GitPreCommitHook.run(git_state.staged_files)


class GitLLMJobBase(LLMJobBase):
    def get_diff(self):
        return git_state.diff

    def perform_base(self, *args, **kwargs) -> str:
        try:
            branch_info = BranchInfoDBAPI.get(Git.get_current_branch())
            purpose = branch_info.purpose
        except DoesNotExist:
            purpose = None
        context_user = {
            "diff": json.dumps(self.get_diff()),
            "purpose": purpose or "No purpose provided",
        }
        return self.process_user_feedback_llm_loop(
            context=self.context,
            context_user=context_user,
        )

    def exec_command(self, *args, **kwargs):
        self.perform_base()


class CommitBody(GitLLMJobBase):
    """This job is used to get an extended commit body for a commit
    message which will be written later.

    This job can be enabled or disabled by using the cli argument
    `--use-commit-body`. It's false by default.

    Template Files:
    ---------------
        commit_body_system.txt: This template is used to get the
            initial information for the llm to understand the task
            it has to do. No Arguments are passed to this template.

        commit_body_user.txt: This template is used to provide the
            user specific information which is used to write the
            extended commit body. The following arguments are passed
            to this template:
                - diff: The diff of the current staged files
                - purpose: The purpose of the current branch

        commit_body_revision.txt: If the LLM response is rejected by
            the user, this template is used to get a revision of the
            LLM response. The LLM will receive the complete previous
            conversation for keeping the context. The following
            arguments are passed to this template:
                - feedback: The feedback from the user
    """

    cli_configurable_name = "use_commit_body"

    def exec_command(self, *args, **kwargs):
        return self.perform_base()


class CommitTitle(GitLLMJobBase):
    """This job is used to perform a commit on all currently staged
    files. A LLM will be used to get the commit title.

    If the cli argument `--use-commit-body` is set, the extended
    commit body will be used as well.

    Template Files:
    ---------------
        commit_title_system.txt: This template is used to get the
            initial information for the llm to understand the task
            it has to do. No Arguments are passed to this template.

        commit_title_user.txt: This template is used to provide the
            user specific information which is used to write the
            commit title. The following arguments are passed to this
            template:
                - diff: The diff of the current staged files
                - purpose: The purpose of the current branch

        commit_title_revision.txt: If the LLM response is rejected by
            the user, this template is used to get a revision of the
            LLM response. The LLM will receive the complete previous
            conversation for keeping the context. The following
            arguments are passed to this template:
                - feedback: The feedback from the user
    """

    def exec_command(self):
        commit_body = CommitBody().perform(self.cli_args, self.kwargs) or None
        commit_title = self.perform_base()
        Git.exec_commit(commit_title, body=commit_body)


class FeedbackOnCommit(GitLLMJobBase):
    """This job is used to get feedback by a LLM for all currently
    staged files. This feedback won't be used for anything, it's
    just for the user.

    This job can be enabled or disabled by using the cli argument
    `--feedback-on-commit`. It's false by default.

    Template Files:
    ---------------
        feedback_on_commit_system.txt: This template is used to get
            the initial information for the llm to understand the
            task it has to do. No Arguments are passed to this
            template.

        feedback_on_commit_user.txt: This template is used to
            provide the user specific information which is used to
            perform the code review. The following arguments are
            passed to this template:
                - diff: The diff of the current staged files
                - purpose: The purpose of the current branch

        feedback_on_commit_revision.txt: If the LLM response is
            rejected by the user (i.e. because the user has questions
            which needs to be explained), this template is used to
            get a revision of the LLM response. The LLM will receive
            the complete previous conversation for keeping the context.
            The following arguments are passed to this template:
                - feedback: The feedback from the user
    """

    cli_configurable_name = "include_ai_feedback"


class CodeReview(GitLLMJobBase):
    """This job will create a code review for the current hash with
    any other. The other hash can be specified by the cli argument
    `--target-branch`.

    Template Files:
    ---------------
        code_review_system.txt: This template is used to get
            the initial information for the llm to understand the
            task it has to do. No Arguments are passed to this
            template.

        code_review_user.txt: This template is used to
            provide the user specific information which is used to
            perform the code review. The following arguments are
            passed to this template:
                - diff: The diff of the current staged files
                - purpose: The purpose of the current branch

        code_review_vision.txt: If the LLM response is
            rejected by the user (i.e. because the user has questions
            which needs to be explained), this template is used to
            get a revision of the LLM response. The LLM will receive
            the complete previous conversation for keeping the context.
            The following arguments are passed to this template:
                - feedback: The feedback from the user
    """

    def get_diff(self):
        target_branch = self.cli_args.target_branch
        diff = Git.get_diff_between_branches(
            branch_1=target_branch,
            branch_2=Git.get_current_branch(),
        )
        return diff
