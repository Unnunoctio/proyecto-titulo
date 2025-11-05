import json

def build_reasoner_prompt(context: str, objective: str, constraints: str, inst_format: str) -> str:
    return f"""
    PROBLEM CONTEXT:
    {context}

    PROBLEM OBJECTIVE:
    {objective}

    PROBLEM CONSTRAINTS:
    {constraints}

    INSTANCE DATA FORMAT:
    {inst_format}

    Task:
    List all the key output variables that are necessary to fully represent the expected result of this problem.
    """

def build_coder_prompt(variables: str) -> str:
    return f"""
    VARIABLES DEFINITIONS:
    {json.dumps(variables, indent = 2)}

    Task:
    Generate the output schema according to the provided variable definitions.
    """