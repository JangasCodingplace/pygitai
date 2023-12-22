# PyGitAI

Welcome to PyGitAI, a tool which helps to improve your code, commit
messages and more by using Git and AI.

This tool is fully integrated in your terminal.


## Why PyGitAI?

PyGitAI is not a super innovative reinvention. There are already some
tools which provide similar features.

The USP of PyGitAI is the level of customization. Which means:

- **Different LLMs can be used**. PyGitAI provides a simple interface
    to integrate your custom LLMs.
- **Prompt customization**. PyGitAI provides a simple interface to
    customize the prompt. This might be useful if you are not happy
    with the default responses provided by PyGitAI or if you'd like
    to enrich the default prompts.
- **No Copy pasting anymore**. Since PyGitAI makes recommendations
    based on your code changes, you don't need to copy paste your
    code changes to a web interface anymore.
- **Matching Company Compliance**. PyGitAI can be customized to match
    your company compliance in many ways. An obvious example is the
    customization of the LLMs. You do not have to send your prompts
    to public APIs. Feel free to use your company provided LLM.


## Getting Started

1. Install via pip: `pip install pygitai`
2. Setup pygitai in your project: `pygitai setup`
3. Check available commands: `pygitai --help`


## CLI Usage

PyGitAI provides several options to improve your workflow.

### Commit:

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


### PR Review:

Get a review by a LLM. A Pull Request is not required. Either a
target branch or a commit hash can be used to get a review.

```
pygitai pr-review \
    --target-branch <TARGET_BRANCH_NAME>
```

- `--target-branch`: The target branch to compare the current branch
    with. This can be a branch name or a commit hash.


### UI

PyGitAI priovides also a graphical user interface which can be used
rather than the CLI. To start the PyGitUI use the following command:

```
pygitai ui
```

This will start a new webserver on port 5000. Open your browser and
navigate to `http://localhost:5000` to use the PyGitUI.


## Customization

PyGitAI provides several options to customize the behavior of the
tool. Any configuration must be specified in `.pygitai/config.ini`
which is available after the setup.

### Default and Fallbacks
Default configuration for PyGitAI:
```
[pygitai]
default_llm_api = OpenAI
default_llm_model = gpt-3.5-turbo
default_prompt_template_dir = pygitai/templates/prompts/OpenAI
```


### Job Specification
This configuration is optional. If not specified, the default
configuration will be used.

```
[pygitai.jobs.<job_name>]
llm_api = <LLM_API>
llm_model = <LLM_MODEL>
prompt_template_dir = <PROMPT_TEMPLATE_DIR>
max_input_tocens = <MAX_INPUT_TOKENS>
```


## Let's make it better together 🤝

Your feedback is essential for improving PyGitAI. By sharing your
thoughts, you help us develop features that meet your needs and
expedite bug fixes.

Thank you for contributing to making PyGitAI better! 👍


## Maintainers

At present, PyGitAI is maintained by

- JangasCofingplace [@JangasCodingplace](https://github.com/JangasCodingplace)[<img src="https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white&label=janis-goesser" align="center">](https://www.linkedin.com/in/janis-goesser-76ba22168/)


## Additional Content

### Videos
**tbd**


## License

This project is licensed under the terms of the [LICENSE](LICENSE).
