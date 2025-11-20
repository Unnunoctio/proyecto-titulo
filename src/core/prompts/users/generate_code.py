
def build_coder_generate_prompt(context: str, objective: str, constraints: str, instance_path: str, instance_format: str, solution_type: str, solution_plan: str, output_schema: str) -> str:
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

SOLUTION METHOD:
{solution_type}

IMPLEMENTATION PLAN:
{solution_plan}

RESULT DATA STRUCTURE (OUTPUT SCHEMA):
{output_schema}

---
TASK:
Generate the code to solve this problem using the solution type and implementation plan instructions provided. The code must follow the provided output_schema format precisely and return ONLY the result - no additional prints, comments, or debug output.

REQUIREMENTS:
1. The code must strictly follow the output schema provided above. 
2. When executed, it must produce **only the final result**, with no extra prints, comments, or debug output. 
3. The implementation must: 
    - Read and process the instance data according to the given path and format. 
    - Apply the algorithmic plan described in the implementation plan. 
    - Handle edge cases and invalid data gracefully. 
    - Return a result matching the defined schema exactly. 
4. Use efficient, clean, and PEP 8-compliant Python code.
"""

def build_coder_fix_prompt(code: str, error: str, fix_plan: str, instance_path: str, instance_format: str, output_schema: str) -> str:
    return f"""
CODE TO FIX:
{code}

CODE ERROR:
{error}

FIX PLAN:
{fix_plan}

INSTANCE INFORMATION:
- Instance file path: {instance_path}
- Instance format: {instance_format}

EXPECTED OUTPUT STRUCTURE (OUTPUT SCHEMA):
{output_schema}

---
TASK:
Fix the code to make it work correctly. The code must follow the provided output_schema format precisely and return ONLY the result - no additional prints, comments, or debug output.
"""

def build_coder_evo_prompt(code: str, improvement_plan: str) -> str:
    return f"""
CODE TO EVOLVE:
{code}

IMPROVEMENT PLAN:
{improvement_plan}

---
TASK:
Apply the improvement plan to the code above.

CRITICAL REQUIREMENTS:
2. Apply every proposed improvement precisely as described.
4. Preserve the original structure, logic, and style everywhere else.
5. Ensure the final code remains complete, runnable, and consistent with the original problem's output schema.
6. Do NOT add explanations, comments, or markdown.
7. Return ONLY the updated Python code, nothing more.

OUTPUT FORMAT:
Return the full corrected code with the improvements applied.
"""