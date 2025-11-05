import yaml
import uuid
import re

from core.models import Provider, Problem, GenerationConfig, GenerationArtifact
from core.providers._base import ProviderBase
from utils.prompt_manager import PromptManager as PM
from utils.code_executor import CodeExecutor as CE


class Agent:
    def __init__(self, problem: Problem, generation_config: GenerationConfig):
        # TODO: Load a Agent Config from a YAML file
        with open("src/problem_config.yaml", "r") as f:
            config = yaml.safe_load(f)

            self.PLANNING_MODEL = self._get_provider(config["agents"]["planning-model"])
            self.CODING_MODEL = self._get_provider(config["agents"]["coding-model"])

        # TODO: Load the problem
        self.PROBLEM = problem

        # TODO: Load the generation config
        self.GENERATION_CONFIG = generation_config

        # TODO: Initialize the generations
        self._ID = str(uuid.uuid4())
        self.GENERATIONS = dict()
        self.BEST_GENERATION = None

        # TODO: Initialize the artifacts
        self.ARTIFACTS = GenerationArtifact(
            output_schema=None,
            constraints_function=None,
            target_function=None
        )

    def _get_provider(self, provider_config: dict) -> ProviderBase:
        if provider_config["provider"] == Provider.OPENAI.value:
            from core.providers.openai import OpenAIProvider

            return OpenAIProvider(provider_config["config"])
        elif provider_config["provider"] == Provider.DEEPSEEK.value:
            from core.providers.deepseek import DeepSeekProvider

            return DeepSeekProvider(provider_config["config"])
        # CLAUDE
        # GEMINI
        else:
            raise Exception(f"Unknown provider: {provider_config['provider']}")
        
    def run(self):
        print("Generating artifacts...")
        self._generate_output_schema()

    def _generate_output_schema(self) -> None:
        # TODO: Generate the output schema
        r_system_prompt = PM.get_system_prompt("reasoner", "output_schema")
        r_user_prompt = PM.get_user_prompt("reasoner", "output_schema", context=self.PROBLEM.context, objective=self.PROBLEM.objective, constraints=self.PROBLEM.constraints, inst_format=self.PROBLEM.inst_format)
        variables_definitions = self.PLANNING_MODEL.generate_response(r_system_prompt, r_user_prompt, temperature=0.3, top_p=0.8)

        print(f"VARIABLES DEFINITIONS:/n{variables_definitions}/n")

        c_system_prompt = PM.get_system_prompt("coder", "output_schema")
        c_user_prompt = PM.get_user_prompt("coder", "output_schema", variables=variables_definitions)
        output_schema = self.CODING_MODEL.generate_response(c_system_prompt, c_user_prompt, temperature=0, top_p=1)
        
        print(f"OUTPUT SCHEMA:/n{output_schema}/n")

        # Store the output schema
        match = re.search(r"```python\n(.*?)```", output_schema, re.DOTALL)
        code = match.group(1) if match else output_schema

        self.ARTIFACTS.output_schema = code

        # Save the output schema in the generations folder
        CE.save_code(file_name="output_schema.py", code=code)

        

