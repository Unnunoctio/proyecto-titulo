from abc import ABC, abstractmethod


class APIBaseLLM(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def generate(self, model: str, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        pass