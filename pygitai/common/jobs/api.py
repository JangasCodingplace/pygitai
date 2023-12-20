import json

from pygitai.common.config import config
from pygitai.common.db_api import BranchInfoDBAPI, DoesNotExist
from pygitai.common.git import Git
from pygitai.common.git import PreCommitHook as GitPreCommitHook
from pygitai.common.git import state as git_state

from .base_job import BaseJob
from .llm_job import LLMJobBase


class AutoStageAll(BaseJob):
    cli_configurable_name = "auto_stage_all"

    def exec_command(self, *args, **kwargs):
        Git.exec_stage_files(["-A"])


class PreCommitHook(BaseJob):
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
    cli_configurable_name = "use_commit_body"

    def exec_command(self, *args, **kwargs):
        return self.perform_base()


class CommitTitle(GitLLMJobBase):
    def exec_command(self):
        commit_body = CommitBody().perform(self.cli_args, self.kwargs) or None
        commit_title = self.perform_base()
        Git.exec_commit(commit_title, body=commit_body)


class FeedbackOnCommit(GitLLMJobBase):
    cli_configurable_name = "include_ai_feedback"


class CodeReview(GitLLMJobBase):
    def get_diff(self):
        target_branch = self.cli_args.target_branch
        diff = Git.get_diff_between_branches(
            branch_1=target_branch,
            branch_2=Git.get_current_branch(),
        )
        return diff
