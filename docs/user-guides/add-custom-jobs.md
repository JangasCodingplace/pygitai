# Add a Custom Job

In some cases, the default jobs provided by pygitai are not enough to
cover all the use cases which are need to support a specific project.
For this reason pygitai provides a simple way to add a custom job
which maches the individual needs.

## Quickstart

Use the following command to create an empty job template:

```
pygitai customization job --type LLM --name MyJob
```

- `--type`: The type of the job to be added.
    Allowed values: `LLM`, `Base`
- `--name`: The name of the job to be added.


This will create a new job file into
`.pygitai/pygitai_customization/job` including a base class for the
new job.

For more information about the classes refer to the following API
docs:

- [JobBase](../api/JobBase.md)
- [LLMJobBase](../api/LLMJobBase.md)


## Example

```python
# Add this class to the .pygitai/pygitai_customization/job directory
from pygitai.common.job.base_job import JobBase


class MyJob(JobBase):
    cli_configurable_name = None

    @classmethod
    def exec_command(self, *args, **kwargs):
        # To be implemented
        pass
```
