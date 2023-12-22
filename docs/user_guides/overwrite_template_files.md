# Overwrite Template Files

In some cases, the default Template files provided by pygitai might
not leads to the desired results. This might be specially true for
custom LLMs.
For this reason, pygitai provides a simple way to overwrite the
default template files.

## Quickstart

Use the following command for overwriting a specific template file:

```
pygitai customization template --llm-job-name MyJob --template-group GROUP
```

- `--llm-job-name`: The name of the llm job to be overwritten
(i.e. `CommitTitle`). Only templates for LLMJobs can be overwritten.
- `--template-group`: The template group to be overwritten.
    Allowed values: `user`, `system`, `revision`

This will create a new template file into
`.pygitai/pygitai_customization/templates`

For more information about the classes refer to the corresponding
LLM Jobs for which the template docs should be overwritten:

- [CodeReview](../presets/JobCodeReview.md)
- [CommitTitle](../presets/JobCommitTitle.md)
- [CommitBody](../presets/JobCommitBody.md)
- [FeedbackOnCommit](../presets/JobFeedbackOnCommit.md)

