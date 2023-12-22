from argparse import Namespace

from pygitai.common.config import BASE_DIR, TOPLEVEL_DIRECTORY
from pygitai.common.utils import camel_to_snake, load_template_file


class Customization:
    def __init__(
        self,
        cli_args: Namespace,
        **kwargs,
    ):
        self.cli_args = cli_args
        self.kwargs = kwargs

    @property
    def template_base_path(self):
        return BASE_DIR / "assets" / "customization_templates"

    @property
    def customization_target_dir(self):
        return TOPLEVEL_DIRECTORY / ".pygitai" / "pygitai_customization"

    def llm(self):
        name = self.cli_args.name
        template_path = self.template_base_path / "llm" / "llm.py.jinja2"
        context = {
            "llm_name": name,
        }

        f = load_template_file(
            template_path=template_path,
            context=context,
        )

        file_name = camel_to_snake(name)
        customization_target_dir = self.customization_target_dir / "llm"
        customization_target_dir.mkdir(exist_ok=True)
        customization_target_file = customization_target_dir / f"{file_name}.py"
        if customization_target_file.exists():
            raise FileExistsError(f"File {customization_target_file} already exists")
        customization_target_file.write_text(f)

    def job(self):
        name = self.cli_args.name
        type_ = self.cli_args.type
        template_file_name = f"{type_}_job.py.jinja2"
        template_path = self.template_base_path / "jobs" / template_file_name
        context = {
            "job_name": name,
        }

        f = load_template_file(
            template_path=template_path,
            context=context,
        )

        file_name = camel_to_snake(name)
        customization_target_dir = self.customization_target_dir / "jobs"
        customization_target_dir.mkdir(exist_ok=True)
        customization_target_file = customization_target_dir / f"{file_name}.py"
        if customization_target_file.exists():
            raise FileExistsError(f"File {customization_target_file} already exists")
        customization_target_file.write_text(f)

    def template(self):
        llm_job_name = self.cli_args.llm_job_name
        template_group = self.cli_args.template_group

        if template_group:
            template_types = [template_group]
        else:
            template_types = ["system", "user", "revision"]

        file_name = camel_to_snake(llm_job_name)
        customization_target_dir = self.customization_target_dir / "templates"
        customization_target_dir.mkdir(exist_ok=True)
        for template_type in template_types:
            customization_target_file = (
                customization_target_dir / f"{file_name}_{template_type}.txt"
            )
            if customization_target_file.exists():
                raise FileExistsError(
                    f"File {customization_target_file} already exists"
                )
            customization_target_file.write_text(
                "EMPTY TEMPLATE. Reffer to the docs for getting available properties."
            )


def main(
    cli_args: Namespace,
    *args,
    **kwargs,
):
    getattr(Customization(cli_args, **kwargs), cli_args.customization_cmd)()
