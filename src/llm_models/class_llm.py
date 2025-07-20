from abc import ABC, abstractmethod
from typing import List, Optional


class LLM(ABC):
    @abstractmethod
    def generate_output_schema(self, problem: str) -> str:
        pass

    @abstractmethod
    def generate_prompt_restrictions(self, problem: str) -> str:
        pass

    @abstractmethod
    def generate_code_restrictions(self, problem: str, prompt: str, input_schema: str) -> str:
        pass

    @abstractmethod
    def generate_code_target_function(self, problem: str, input_schema: str) -> str:
        pass

    @abstractmethod
    def generate_first_problems_prompts(self, problem: str, output_schema: str, num_prompts: int) -> List[str]:
        pass

    @abstractmethod
    def generate_code(self, problem: str, prompt: str, output_schema: str, inspiration: Optional[str] = None) -> str:
        pass
    
    @abstractmethod
    def generate_prompt_evolution(self, problem: str, code: str) -> str:
        pass
    
    @abstractmethod
    def generate_evolution_code(self, problem: str, output_schema: str, code: str, list_improvements: str) -> str:
        pass
