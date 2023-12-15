import os
from dataclasses import dataclass


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

    @classmethod
    def from_env(cls) -> "OpenAIConfig":
        return cls(
            openai_key_name=os.environ["OPENAI_KEY_NAME"],
            openai_key_secret=os.environ["OPENAI_KEY_SECRET"],
            openai_model=os.environ["OPENAI_MODEL"],
        )


@dataclass(frozen=True)
class Config:
    git: Git
    openai: OpenAIConfig
    logger: Logger

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            git=Git.from_env(),
            openai=OpenAIConfig.from_env(),
            logger=Logger.from_env(),
        )


config = Config.from_env()
