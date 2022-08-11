import imp
from pydantic import BaseModel
import contextvars
from loguru import logger
import json

config_context = contextvars.ContextVar("lbots_secrets")


class FacePPConfig(BaseModel):
    api_key: str = ""
    api_secret: str = ""


class ApiConfigs(BaseModel):
    facepp: FacePPConfig = FacePPConfig()
    ai: str = ""

    @classmethod
    def from_file(cls, config_file):
        with open(config_file, "r") as f:
            configs = json.load(f)
        return cls(**configs)

    def to_file(self, config_file):
        with open(config_file, "w") as f:
            json.dump(self.dict(), f, indent=4)


def init_configs(config_file):
    logger.info(f"Loading configs from {config_file}")
    configs = ApiConfigs.from_file(config_file)
    logger.success(f"Configs loaded")
    config_context.set(configs)
    logger.success(f"Configs global variable set")


def get_config() -> ApiConfigs:
    resp = config_context.get()
    if isinstance(resp, ApiConfigs):
        return resp
