import json

from pygitai.common.config import config
from pygitai.common.db_api import BranchInfoDBAPI
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
        branch_info = BranchInfoDBAPI.get(Git.get_current_branch())
        context_user = {
            "diff": json.dumps(git_state.diff),
            "purpose": branch_info.purpose or "No purpose provided",
        }
        return self.process_user_feedback_llm_loop(
            context=self.context,
            context_user=context_user,
        )

    def exec_command(self, *args, **kwargs):
        self.perform_base()


class CommitTitle(GitLLMJobBase):
    def exec_command(self):
        commit_title = self.perform_base()
        Git.exec_commit(commit_title)


class FeedbackOnCommit(GitLLMJobBase):
    cli_configurable_name = "feedback_on_commit"


class CodeReview(GitLLMJobBase):
    cli_configurable_name = "feedback_on_commit"

    def get_diff(self):
        target_branch = self.cli_args.target_branch
        return Git.get_diff_between_branches(
            branch_1=target_branch,
            branch_2=Git.get_current_branch(),
        )
