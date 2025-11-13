
def build_reasoner_prompt(context: str, objective: str, constraints: str, num_methods: int) -> str:
    return f"""
PROBLEM DESCRIPTION:
{context}

OBJECTIVE:
{objective}

CONSTRAINTS:
{constraints}

---
TASK:
Identify and rank the top {num_methods} algorithmic or heuristic solution approaches that are most suitable for solving this problem effectively.

INSTRUCTIONS:
- Base your reasoning on the problem type, objective, and key constraints.
- Include only methods that are realistically applicable and scalable.
- Consider both exact algorithms and metaheuristic approaches where relevant.
- Order them by expected effectiveness and feasibility.
- Output only a valid Python list of dictionaries as described in the system prompt.
- Do not include explanations, markdown, or any text outside the list.
"""