
def build_reasoner_prompt(code: str, error: str, result: str | None, instance_path: str, instance_format: str, output_schema: str) -> str:
    return f"""
CODE TO ANALYZE:
{code}

ERROR DESCRIPTION:
{error}

OBSERVED RESULT OR TRACEBACK:
{result}

INSTANCE INFORMATION:
- Instance file path: {instance_path}
- Instance format: {instance_format}

EXPECTED OUTPUT STRUCTURE (OUTPUT SCHEMA):
{output_schema}

---
TASK:
You must analyze the code, the observed error, and the result above, and generate a FIX PLAN following the required FIX PLAN format exactly.

GUIDELINES:
- Base your reasoning strictly on the provided information — do not speculate or invent missing details.
- Identify the most probable technical cause(s) of failure.
- For each root cause, describe the corrective actions needed and where to apply them.
- Use the expected output schema only to validate the intended result type or structure, not to rewrite code.
- If multiple issues are present, include separate Root cause sections for each.
- Keep the FIX PLAN concise and fully self-contained.
"""