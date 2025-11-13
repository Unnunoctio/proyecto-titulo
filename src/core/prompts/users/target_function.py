
def build_reasoner_prompt(context: str, objective: str, input_data_structure: str) -> str:
    return f"""
PROBLEM DESCRIPTION:
{context}

OBJECTIVE:
{objective}

RESULT DATA STRUCTURE:
{input_data_structure}

---
TASK:
Analyze the problem and the objective function to determine the evaluation logic needed to compare multiple candidate solutions.

INSTRUCTIONS:
- Identify what makes one solution better than another.
- Consider both direct (explicit) and indirect (derived or implied) evaluation criteria.
- Specify how ties between solutions should be resolved.
- Focus only on reasoning and directive formulation — do not write code.

OUTPUT:
Provide a structured list of evaluation directives that clearly define the criteria and priorities
the system should use to determine the best solution.
"""

def build_coder_prompt(context: str, objective: str, evaluation_directives: str, input_data_structure: str) -> str:
    return f"""
PROBLEM DESCRIPTION:
{context}

OBJECTIVE:
{objective}

EVALUATION DIRECTIVES:
{evaluation_directives}

INPUT FORMAT (candidate list):
[
    {input_data_structure},
    ...
]

---
TASK:
Generate the `target_function` that evaluates all solution candidates based on the provided directives and returns the **index (int)** of the best-performing solution in the list.

REQUIREMENTS:
- Follow all evaluation directives (explicit and implicit).
- Compare solutions according to the problem's objective.
- If objective scores are equal, prefer the one with smaller execution time.
- Include all necessary imports.
- Output only the complete, executable function code.
"""