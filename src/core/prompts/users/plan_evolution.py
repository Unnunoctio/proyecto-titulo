
def build_reasoner_prompt(context: str, objective: str, constraints: str, instance_path: str, instance_format: str, solution_type: str, code: str) -> str:
    return f"""
PROBLEM TO SOLVE:
DESCRIPTION:
{context}

OBJECTIVE:
{objective}

CONSTRAINTS:
{constraints}

INSTANCE DATA PATH:
- Instance file path: {instance_path}
- Instance format: {instance_format}

METHOD TO SOLVE THIS PROBLEM:
{solution_type}

CODE TO ANALYZE:
{code}

---
TASK:
Analyze the code above and generate an IMPROVEMENT PLAN following the required format.

Your goal is to:
- Identify the single most impactful code region whose improvement will significantly enhance correctness and objective-function performance.
- Provide actionable, specific improvements with clear reasoning.
- Include safety and validation considerations to ensure correctness after the modification.

Return ONLY the IMPROVEMENT PLAN block.
"""