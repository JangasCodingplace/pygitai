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


@dataclass(frozen=True)
class Git:
    pre_commit: bool

    @classmethod
    def from_env(cls) -> "Git":
        use_pre_commit = os.environ.get("PYGIT_PRE_COMMIT", "false").lower() == "true"
        return cls(pre_commit=use_pre_commit)


@dataclass(frozen=True)
class Logger:
    level: str

    @classmethod
    def from_env(cls) -> "Logger":
        return cls(level=os.environ.get("PYGIT_LOG_LEVEL", "INFO"))


@dataclass(frozen=True)
class OpenAIConfig:
    openai_key_name: str
    openai_key_secret: str
    openai_model: str
    openai_api_token_limit: int

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        return cls(
            openai_key_name=os.environ["OPENAI_KEY_NAME"],
            openai_key_secret=os.environ["OPENAI_KEY_SECRET"],
            openai_model=os.environ["OPENAI_MODEL"],
            openai_api_token_limit=int(os.environ.get("OPENAI_API_TOKEN_LIMIT", 4096)),
        )


@dataclass(frozen=True)
class GeneralConfig:
    base_dir: Path = BASE_DIR
    template_dir: Path = BASE_DIR / "templates"
    db_name: Path = TOPLEVEL_DIRECTORY / ".pygitai" / "pygitaidb.sqlite3"

    @classmethod
    def from_env(cls) -> "GeneralConfig":
        return cls()


@dataclass(frozen=True)
class Config:
    general: GeneralConfig
    git: Git
    openai: OpenAIConfig
    logger: Logger

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            general=GeneralConfig.from_env(),
            git=Git.from_env(),
            openai=OpenAIConfig.from_env(),
            logger=Logger.from_env(),
        )


config = Config.from_env()