from abc import ABC, abstractmethod


class ProviderBase(ABC):
    @abstractmethod
    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0, top_p: float = 1.0) -> str:
        pass