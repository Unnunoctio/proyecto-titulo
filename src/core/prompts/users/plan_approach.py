
def build_reasoner_prompt(context: str, objective: str, constraints: str, instance_path: str, instance_format: str, approach_name: str) -> str:
    return f"""
PROBLEM DESCRIPTION:
{context}

OBJECTIVE:
{objective}

CONSTRAINTS:
{constraints}

INSTANCE INFORMATION:
- Instance file path: {instance_path}
- Instance format: {instance_format}

SELECTED METHOD:
{approach_name}

---
TASK:
Generate a detailed, technically actionable **Implementation Plan** describing how to implement the selected algorithmic or heuristic method to solve this problem.

INSTRUCTIONS:
- Base your plan on the provided problem context, objective, constraints, and selected method.
- Focus on defining **what** each stage of the implementation should accomplish — not how to code it.
- Include all essential components: data loading, preprocessing, initialization, main loop or optimization logic, stopping criteria, and output generation.
- Each step must be **method-specific**, **sequential**, and **self-contained**.
- Avoid pseudocode, syntax, or explanatory commentary.

Output only the plan, in plain text, with no extra sections or formatting.
"""