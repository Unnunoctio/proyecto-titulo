from dataclasses import dataclass
from typing import Optional, Dict

@dataclass
class Problem:
    context: str
    objective: str
    constraints: Optional[str]
    instance_filename: Optional[str]
    instance_format: Optional[str]

@dataclass
class GenerationConfig:
    first_generation_size: int
    max_epochs: int
    evolution_strategy: str # "individual" | "cross"
    selection_strategy: str # "best-by-solution" | "all-by-solution"
    timeout: int # seconds
    max_errors_resolved: int # max number of errors resolved in a single generation

@dataclass
class CodeGenerated:
    code_id: str
    father_code_id: Optional[str]
    epoch: int
    solution_type: str
    solution_cross: str
    version: float # version of the code, starting at 1.0 and incrementing by 0.1 for each new generation of the same problem with error
    code_path: str # path to the code file, create to "solution_main"_"epoch"_"cross"_"version".py
    result: dict
    execution_time: float
    error: Optional[str]

@dataclass
class GenerationRun:
    generation_id: str
    problem: Problem
    generation_config: GenerationConfig
    generations: Dict[str, CodeGenerated]
    best_generation: Optional[CodeGenerated]

@dataclass
class ArtifactGenerated:
    output_schema: Optional[str]
    constraints_function: Optional[str]
    target_function: Optional[str]
