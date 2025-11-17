
def build_reasoner_prompt(context: str, constraints: str, instance_path: str, instance_format: str) -> str:
    return f"""
PROBLEM TO ANALYZE:
DESCRIPTION:
{context}

CONSTRAINTS:
{constraints}

INSTANCE INFORMATION:
- Instance file path: {instance_path}
- Instance format: {instance_format}
(The instance file must be loaded and its data validated against the result structure.)


---
TASK:
Based on the problem description above, extract and prioritize ALL constraints following the system instructions.
"""

def build_coder_prompt(context: str, list_of_constraints: str, result_data_structure: str, instance_path: str, instance_format: str) -> str:
    return f"""
PROBLEM DESCRIPTION:
{context}

LIST OF CONSTRAINTS:
{list_of_constraints}

RESULT DATA STRUCTURE:
{result_data_structure}

INSTANCE INFORMATION:
- Instance file path: {instance_path}
- Instance format: {instance_format}
(The instance file must be loaded and its data validated against the result structure.)

---
TASK:
Generate the 'validate_restrictions' function that verifies ALL constraints from the problem description. Following the provided format specification.
"""