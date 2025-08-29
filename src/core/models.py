from dataclasses import dataclass
from typing import Optional

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
    selection_strategy: str # "best-by-solution" | "best-by-epoch"
    timeout: int # seconds

@dataclass
class CodeGenerated:
    code_path: str
    solution_type: str
    result: dict
    execution_time: float
    error: Optional[str]
