from typing import List, Optional

from openai import OpenAI

from llm_models.class_llm import LLM


class Openia_LLM(LLM):
    def __init__(self):
        self.API_KEY = "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"
        self.MODEL_NAME = "gpt-4.1-mini"
        self.client = OpenAI(api_key=self.API_KEY)

    def generate_output_schema(self, problem: str) -> str:
        system_prompt = """
Regarding the stated problem, it is requested to define a unified output structure (e.g., an object or dictionary) that standardizes the format of the results.
- The structure must be compatible with the Python language.
- Define only the structure.
- Define the variables in English, as standard.
- Add comments explaining the meaning of each variable within the same structure.
- DO NOT provide examples.
- DO NOT add additional text.
- DO NOT add additional comments.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": problem},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=0.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating output schema: {e}")
            raise e

    def generate_prompt_restrictions(self, problem: str) -> str:
        system_prompt = """
Regarding the described problem, you must generate a list with all the constraints contained in the problem.
- The list must be ordered by priority.
- The list must contain only text strings.
- Each constraint must appear on a separate line.
- Each constraint must follow a specific format.
- The list must be written in English.
"""

        user_prompt = f"""
-------------PROBLEM-------------
{problem}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=1.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating prompt restrictions: {e}")
            raise e

    def generate_code_restrictions(self, problem: str, prompt: str, input_schema: str) -> str:
        system_prompt = """
Regarding the described problem, you must generate a Python function that validates all the constraints contained in the problem.
- The function must be written in Python.
- The function must be complete and executable.
- The name of the function must be "validate_restrictions".
- The function must receive a parameter named "result", which follows the input_schema format.
- The function must return a Tuple[bool, str], indicating whether the result satisfies all the problem's constraints; if not, the string must explain the reason.
- The explanation of the error must be written in English.
- All text must follow UTF-8 encoding.
- Only generate the function code — do not execute it.
- Important: The function must verify that the values used in the result are derived from the input instance and do not invent or introduce arbitrary data.
"""
        user_prompt = f"""
-------------PROBLEM-------------
{problem}
-------------PROMPT-------------
{prompt}
-------------INPUT SCHEMA-------------
{input_schema}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=0.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating validate restrictions: {e}")
            raise e

    def generate_code_target_function(self, problem: str, input_schema: str) -> str:
        system_prompt = """
Write a Python function named target_function(result). This function must evaluate a result object, which represents the output generated by a proposed solution to a given problem.
The function should compute a quality score based on how well the result meets the problem's objectives. The score must be a numerical value (e.g., on a scale from 0 to 100, or any other defined quantitative metric).
The design of the function should consider the following aspects:
- The name of the function must be "target_function".
- The function must receive a parameter named "result", which follows the input_schema format.
- Clear evaluation criteria: Explain which characteristics of result are being assessed (e.g., accuracy, efficiency, coverage, penalties, etc.).
- Expected return value: A number representing the quality of the solution. It can be either an int or a float.
- Compatibility: The code must be executable, follow UTF-8 encoding, and be written in Python 3.
- Error handling or exceptions: In case of an error or invalid input, the function may either return a score of 0 or raise an exception with an error message in English.
"""

        user_prompt = f"""
-------------PROBLEM-------------
{problem}
-------------INPUT SCHEMA-------------
{input_schema}
"""
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=1.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating prompt restrictions: {e}")
            raise e

    def generate_first_problems_prompts(self, problem: str, output_schema: str, num_prompts: int) -> List[str]:
        system_prompt = f"""
Regarding the stated problem, generate {num_prompts} different prompts for code creation to solve the problem, specifying in the prompt that:
- The code must be developed in Python.
- The code must be generated in such a way that, when executed, it only returns the result and does not print additional information.

Each prompt must be separated by a line of 25 "#" symbols, to make them easy to distinguish.
Each prompt must approach the problem using different methods, such as heuristics, metaheuristics, exact algorithms, among others.
Each prompt must be completely independent of the others.
Each prompt must be written in English.
Each prompt must be added step by step instructions to solve the problem.
Each prompt must be added output schema in the prompt.
Each prompt must not provide examples.
Each prompt must not add additional text.
Each prompt must not add additional comments.

Each prompt must follow the specified output structure in the following format:
{output_schema}

IMPORTANT: ONLY return the {num_prompts} prompts.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": problem},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=1.5,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            prompts = []
            for prompt in content.split(25 * "#"):
                cleaned_prompt = prompt.strip()
                if cleaned_prompt:
                    prompts.append(cleaned_prompt)

            return prompts
        except Exception as e:
            print(f"Error generating problems prompts: {e}")
            raise e

    def generate_code(self, problem: str, prompt: str, output_schema: str, inspiration: Optional[str] = None) -> str:
        system_prompt = """
You are a Python developer.
Your task is to write a Python code that solves the stated problem:
- The code must be written in Python.
- The code must be complete and executable.
- The result should adhere to the following output_schema format.
- The code must be generated in such a way that, when executed, it only returns the result.
- The code only print the result to the console.
- The code must not print additional information.
"""
        user_prompt = f"""
-------------PROBLEM-------------
{problem}
-------------INSPIRATION-------------
{inspiration}
-------------PROMPT-------------
{prompt}
-------------OUTPUT SCHEMA-------------
{output_schema}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=0.0,
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating code: {e}")
            raise e
