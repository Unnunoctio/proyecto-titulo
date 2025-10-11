import yaml

from core.experts.api_base import APIBaseExpert
from core.models import GenerationConfig, Problem

with open("src/config.yaml", "r") as f:
    config = yaml.safe_load(f)

PROBLEM = Problem(
    context=config["problem"]["context"],
    objective=config["problem"]["objective"],
    constraints=config["problem"]["constraints"],
    instance_filename=config["problem"]["instance-filename"],
    instance_format=config["problem"]["instance-format"],
)

GENERATION_CONFIG = GenerationConfig(
    first_generation_size=config["generation"]["first-generation-size"],
    max_epochs=config["generation"]["max-epochs"],
    evolution_strategy=config["generation"]["evolution-strategy"],
    selection_strategy=config["generation"]["selection-strategy"],
    timeout=config["generation"]["timeout"],
    max_errors_resolved=config["generation"]["max-errors-resolved"],
)

with open("src/core/experts/config.yaml", "r") as f:
    experts_config = yaml.safe_load(f)

expert = APIBaseExpert(experts_config["experts"][0])
expert.run_expert(problem=PROBLEM, generation_config=GENERATION_CONFIG)
