from abc import ABC, abstractmethod
from typing import List


class LLM(ABC):
    @abstractmethod
    def generate_output_schema(self, problem: str) -> str:
        pass

    @abstractmethod
    def generate_first_problems_prompts(self, problem: str, output_schema: str) -> List[str]:
        pass

    @abstractmethod
    def generate_code(self, prompt: str) -> str:
        pass
