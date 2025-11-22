from enum import Enum
from dataclasses import dataclass
from typing import Optional
import json

class Provider(Enum):
    OPENAI = "OPENAI"
    CLAUDE = "CLAUDE"
    GEMINI = "GEMINI"
    DEEPSEEK = "DEEPSEEK"

@dataclass
class Problem:
    context: str
    objective: str
    constraints: Optional[str]
    inst_filename: Optional[str]
    inst_format: Optional[str]

@dataclass
class GenerationConfig:
    first_gen_size: int
    max_epochs: int
    evo_strategy: str # "individual" | "cross"
    select_strategy: str # "best" | "random"
    timeout: int = 30 # seconds
    max_errors: int = 5 # number of errors before closing the generation

@dataclass
class GenerationCode:
    _id: str
    father_id: Optional[str]
    epoch: int
    version: int # version of the code, starting from 1 and incrementing by 1 for each new version of the code
    solution_type: str
    solution_cross: Optional[str]
    code_path: str # path to the code file
    code_output: Optional[dict] # output of the code run
    code_time: float # time taken to run the code
    code_error: Optional[str] # error message if the code failed to run

@dataclass
class GenerationArtifact:
    output_schema: Optional[str] # schema of the output
    constraints_function: Optional[str] # function that checks if the output satisfies the constraints
    target_function: Optional[str] # function that checks if the output is the target

class DataclassJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Exception):
            return str(obj)
        if isinstance(obj, tuple):
            return str(obj)  # o list(obj) si prefieres arrays
        return super().default(obj)
    
    def encode(self, obj):
        # Convierte recursivamente todas las tuplas-clave a strings
        def convert_keys(o):
            if isinstance(o, dict):
                return {str(k) if isinstance(k, tuple) else k: convert_keys(v) 
                        for k, v in o.items()}
            elif isinstance(o, list):
                return [convert_keys(item) for item in o]
            elif isinstance(o, tuple):
                return str(o)  # o list(o)
            return o
        
        return super().encode(convert_keys(obj))