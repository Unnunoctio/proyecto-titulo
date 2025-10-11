import yaml

from core.models import Provider
from core.providers._base import ProviderBase


class Agent:
    def __init__(self):
        # TODO: Load a Agent Config from a YAML file
        with open("src/core/agent/config.yaml", "r") as f:
            config = yaml.safe_load(f)

            self.CODING_MODEL = self._get_provider(config["agent"]["coding-model"])
            self.PLANNING_MODEL = self._get_provider(config["agent"]["planning-model"])

    def _get_provider(self, provider_config: dict) -> ProviderBase:
        if provider_config["provider"] == Provider.OPENAI:
            from core.providers.openai import OpenAIProvider

            return OpenAIProvider(provider_config["config"])
        elif provider_config["provider"] == Provider.DEEPSEEK:
            from core.providers.deepseek import DeepSeekProvider

            return DeepSeekProvider(provider_config["config"])
        # CLAUDE
        # GEMINI
        else:
            raise Exception(f"Unknown provider: {provider_config['provider']}")
        
    def run_agent(self, problem: Problem, generation_config: GenerationConfig) -> 
