from typing import Dict, Any
from llm.api_base import APIBaseLLM
from llm.openai import OpenAILLM

class APIBaseExpert():
    def __init__(self, config: Dict[str, Any]):
        self.name = config.get("name")
        self.standard_model = config.get("standard-model")
        self.coding_model = config.get("coding-model")
        self.reasoning_model = config.get("reasoning-model")

        if config.get("library") == "openai":
            self.llm: APIBaseLLM = OpenAILLM(config.get("api-key"))
        else:
            raise Exception(f"Unknown library: {config.get('library')}")
    
    def run_expert(self, problem: object) -> None:
        pass



