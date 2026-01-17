
def build_reasoner_prompt(context: str, objective: str, constraints: str, instance_path: str, instance_format: str, solution_type: str, code: str, current_solution: dict, best_solution: dict) -> str:
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

YOUR RESULT:
{current_solution}

BEST CURRENT RESULT:
{best_solution}

---
TASK:
Analyze the code above and generate an IMPROVEMENT PLAN following the required format.

Your goal is to:
- Analyze the current result and the best result.
- Matches or exceeds the current best-known result for the problem.
- Identify the single most impactful code region whose improvement will significantly enhance correctness and objective-function performance.
- Provide actionable, specific improvements with clear reasoning.
- Include safety and validation considerations to ensure correctness after the modification.

Return ONLY the IMPROVEMENT PLAN block.
"""