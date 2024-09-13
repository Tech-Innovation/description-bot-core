from dataclasses import dataclass
from typing import List
from clients.streaming import StreamingConfig
from configuration.config_manager import ConfigManager


class Config:
    """
    Configuration class that initializes and loads various configurations
    using the ConfigManager.
    """

    def __init__(self, config_file):
        self.config_manager = ConfigManager(config_file)

        self.inputs = Inputs(
            source=self.config_manager.get("INPUTS", "source"),
            company_settings=self.config_manager.get("INPUTS", "company_settings"),
        )

        self.streaming = StreamingConfig(
            enabled=self.config_manager.getboolean("STREAMING", "streaming_enabled"),
            url=self.config_manager.get("STREAMING", "streaming_url"),
        )

        self.params = Params(
            model=self.config_manager.get("PARAMS", "model"),
            query=self.config_manager.get("PARAMS", "query"),
        )


@dataclass
class Inputs:
    source: str
    company_settings: str


@dataclass
class Params:
    model: str
    query: str
