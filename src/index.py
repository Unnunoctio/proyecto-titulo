import yaml
import asyncio
import time

from core.agent import Agent
from core.models import Problem, GenerationConfig

start_time = time.time()

problem_path = "src/problem_config.yaml"

with open(problem_path, "r") as f:
    config = yaml.safe_load(f)

    problem = Problem(
        context=config["problem"]["context"],
        objective=config["problem"]["objective"],
        constraints=config["problem"]["constraints"],
        inst_filename=config["problem"]["instance-filename"],
        inst_format=config["problem"]["instance-format"]
    )

    generation_config = GenerationConfig(
        first_gen_size=config["generation"]["first-generation-size"],
        max_epochs=config["generation"]["max-epochs"],
        evo_strategy=config["generation"]["evolution-strategy"],
        select_strategy=config["generation"]["selection-strategy"],
        timeout=config["generation"]["timeout"],
        max_errors=config["generation"]["max-errors"]
    )

agent = Agent(problem, generation_config)
asyncio.run(agent.run())

print(f"Total time: {time.time() - start_time} seconds")