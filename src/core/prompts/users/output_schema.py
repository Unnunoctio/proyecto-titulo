
def build_coder_prompt(context: str, objective: str, constraints: str) -> str:
    return f"""
PROBLEM TO SOLVE:
{context}

OBJECTIVE:
{objective}

CONSTRAINTS:
{constraints}

---
TASK:
Generate the appropriate output schema following the system instructions.
"""