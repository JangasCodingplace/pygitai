import configparser
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# duplicate code from pygitai/common/git.py to avoid circular imports
TOPLEVEL_DIRECTORY = Path(
    subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        stdout=subprocess.PIPE,
        text=True,
    ).stdout.strip()
)


def read_config_file() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    default_config_file_path = TOPLEVEL_DIRECTORY / "pygitai.ini"
    config.read(default_config_file_path)
    config_file_path = TOPLEVEL_DIRECTORY / ".pygitai" / "config.ini"
    config.read(config_file_path)
    return config


@dataclass(frozen=True)
class Git:
    pre_commit: bool = (TOPLEVEL_DIRECTORY / ".git" / "hooks" / "pre-commit").exists()

    @classmethod
    def from_env(cls) -> "Git":
        return cls()


@dataclass(frozen=True)
class Logger:
    level: str

    @classmethod
    def from_env(cls) -> "Logger":
        return cls(level=os.environ.get("PYGIT_LOG_LEVEL", "INFO"))


@dataclass(frozen=True)
class OpenAIConfig:
    openai_key_name: str | None
    openai_key_secret: str | None
    openai_model: str | None
    openai_api_token_limit: int

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        return cls(
            openai_key_name=os.getenv("OPENAI_KEY_NAME"),
            openai_key_secret=os.getenv("OPENAI_KEY_SECRET"),
            openai_model=os.getenv("OPENAI_MODEL"),
            openai_api_token_limit=int(os.getenv("OPENAI_API_TOKEN_LIMIT", 4096)),
        )


@dataclass(frozen=True)
class HuggingFaceConfig:
    api_token: str | None
    model: str | None

    @classmethod
    def from_env(cls) -> "HuggingFaceConfig":
        return cls(
            api_token=os.getenv("HUGGING_FACE_API_TOKEN"),
            model=os.getenv("HUGGING_FACE_MODEL", "microsoft/codereviewer"),
        )


@dataclass(frozen=True)
class GeneralConfig:
    llm: str

    base_dir: Path = BASE_DIR
    template_dir: Path = BASE_DIR / "templates"
    db_name: Path = TOPLEVEL_DIRECTORY / ".pygitai" / "pygitaidb.sqlite3"
    cfg: configparser.ConfigParser = read_config_file()
    toplevel_directory = TOPLEVEL_DIRECTORY

    @classmethod
    def from_env(cls) -> "GeneralConfig":
        return cls(
            llm=os.environ.get("PYGITAI_LLM", "OpenAI"),
        )


@dataclass(frozen=True)
class Config:
    general: GeneralConfig
    git: Git
    openai: OpenAIConfig
    hugging_face: HuggingFaceConfig
    logger: Logger

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            general=GeneralConfig.from_env(),
            git=Git.from_env(),
            openai=OpenAIConfig.from_env(),
            hugging_face=HuggingFaceConfig.from_env(),
            logger=Logger.from_env(),
        )


config = Config.from_env()
