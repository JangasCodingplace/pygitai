import shutil

from pygitai.common.config import BASE_DIR, config
from pygitai.common.db_api import BranchInfoDBAPI
from pygitai.common.git import Git


def pygit_setup():
    toplevel_directory = Git.get_toplevel_directory()
    pygitai_project_config_dir = toplevel_directory / ".pygitai"
    pygitai_project_config_dir.mkdir(exist_ok=True)
    # add .gitignore to pygitai directory if it doesn't exist
    pygitai_gitignore_file = pygitai_project_config_dir / ".gitignore"
    if not pygitai_gitignore_file.exists():
        pygitai_gitignore_file.write_text("# Created by pygitai automatically.\n*")

    # create config.ini if it doesn't exist
    pygitai_config_file = pygitai_project_config_dir / "config.ini"
    if not pygitai_config_file.exists():
        pygitai_default_config_file = BASE_DIR / "assets" / "config.ini"
        pygitai_default_config_file_contents = pygitai_default_config_file.read_text()
        pygitai_config_file.write_text(pygitai_default_config_file_contents)

    # create pygitai_customizations directory if it doesn't exist by copying from assets
    pygitai_customizations_dir = pygitai_project_config_dir / "pygitai_customization"
    if not pygitai_customizations_dir.exists():
        pygitai_customizations_assets_dir = (
            BASE_DIR / "assets" / "pygitai_customization"
        )
        shutil.copytree(pygitai_customizations_assets_dir, pygitai_customizations_dir)

    if not config.general.db_name.exists():
        BranchInfoDBAPI.create_table_if_not_exists()


def main(
    *args,
    **kwargs,
):
    pygit_setup()
