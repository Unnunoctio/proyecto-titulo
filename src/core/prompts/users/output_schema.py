import json

def build_reasoner_prompt(context: str, objective: str, constraints: str) -> str:
    return f"""
PROBLEM TO SOLVE:
{context}

OBJECTIVE:
{objective}

CONSTRAINTS:
{constraints}

---
TASK:
List all output variables that the solution must contain, following the system rules.
"""

def build_coder_prompt(variables: str) -> str:
    return f"""
VARIABLES DEFINITIONS:
{json.dumps(variables, indent = 2)}

---
TASK:
Generate the Python `output_schema` according to the system instructions.
"""