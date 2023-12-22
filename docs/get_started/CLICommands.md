# Predefined CLI Commands of PyGitAI

PyGitAI has a set of predefined CLI commands that can be used to
perform common tasks and support you as a developer as good as
possible.


## setup-project

Setup a new pygitai project in the toplevel directory of your current
Project.

```
pygitai setup-project
```

This allows you to customize the pygitai configuration for your
project. Reffer to our customization guide for more information:

- [Add a Custom Job](../user_guides/add_custom_jobs.md)
- [Add a Custom Command](../user_guides/add_custom_commands.md)
- [Overwrite Template Files](../user_guides/overwrite_template_files.md)


## setup-branch

Enrich the current branch with some additional information which can
be used by PyGitAI LLMs to get better results.

```
pygitai setup-branch
```


## commit

Commit the current code changes and generate a commit message based
on a LLM response.

```
pygitai commit  \
    [--use-commit-body] \
    [--include-ai-feedback] \
    [--auto-stage-all]
```

- `--use-commit-body`: Add extended information to a commit by using
    the commit body. Default: `False`
- `--include-ai-feedback`: Get AI feedback based on the currently
    staged changes. Default: `False`
- `--auto-stage-all`: Automatically stage all changes.
    Default: `False`


## pr-review

Get a review by a LLM. A Pull Request is not required. Either a
target branch or a commit hash can be used to get a review.

```
pygitai pr-review \
    --target-branch <TARGET_BRANCH_NAME>
```

- `--target-branch`: The target branch to compare the current branch
    with. This can be a branch name or a commit hash.


## customization

Helper to generate customization presets.

### Job

Generate a new job template.

```
pygitai customization job \
    --type <JOB_TYPE> \
    --name <JOB_NAME>
```

- `--type`: The type of the job to be added.
    Allowed values: `LLM`, `Base`
- `--name`: The name of the job to be added.

For more information about the classes refer to the user guide
[Add a Custom Job](../user_guides/add_custom_jobs.md).


### LLM

Generate a new LLM template.

```
pygitai customization llm \
    --name <LLM_NAME>
```

- `--name`: The name of the LLM to be added.

For more information about the classes refer to the user guide
[Add a Custom LLM](../user_guides/add_custom_llm.md).


### Template

Generate a new template file.

```
pygitai customization template \
    --llm-job-name <LLM_JOB_NAME> \
    --template-group <TEMPLATE_GROUP>
```

- `--llm-job-name`: The name of the llm job to be overwritten
(i.e. `CommitTitle`). Only templates for LLMJobs can be overwritten.
- `--template-group`: The template group to be overwritten.
    Allowed values: `user`, `system`, `revision`

For more information about the classes refer to the user guide
[Overwrite Template Files](../user_guides/overwrite_template_files.md).


## PyGitUI

PyGitAI priovides also a graphical user interface which can be used
rather than the CLI. To start the PyGitUI use the following command:

```
pygitai ui
```

This will start a new webserver on port 5000. Open your browser and
navigate to `http://localhost:5000` to use the PyGitUI.
