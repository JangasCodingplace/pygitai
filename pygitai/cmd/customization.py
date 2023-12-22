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
        template_path = self.template_base_path / "llm.py.jinja2"
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


def main(
    cli_args: Namespace,
    *args,
    **kwargs,
):
    getattr(Customization(cli_args, **kwargs), cli_args.customization_cmd)()