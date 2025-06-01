from typing import List

from openai import OpenAI

from llm_models.class_llm import LLM


class Deepseek_LLM(LLM):
    API_KEY = "sk-b097087195764609aa93a5ceb58cbd9f"
    client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

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
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": problem},
                ],
                stream=False,
                response_format={"type": "text"},
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating output schema: {e}")
            raise e

    def generate_first_problems_prompts(self, problem: str, output_schema: str) -> List[str]:
        system_prompt = f"""
Regarding the stated problem, generate 10 different prompts for code creation to solve the problem, specifying in the prompt that:
- The code must be developed in Python.
- The code must be generated in such a way that, when executed, it only returns the result and does not print additional information.

Each prompt must be separated by a line of 25 "#" symbols, to make them easy to distinguish.
Each prompt must approach the problem using different methods, such as heuristics, metaheuristics, exact algorithms, among others.
Each prompt must be completely independent of the others.
Each prompt must be written in English.
Each prompt must follow the specified output structure in the following format:
{output_schema}

- ADD step by step instructions to solve the problem.
- ADD output schema in the prompt.
- DO NOT provide examples.
- DO NOT add additional text.
- DO NOT add additional comments.
- ONLY return the 10 prompts.
"""

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": problem},
                ],
                stream=False,
                response_format={"type": "text"},
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

    def generate_code(self, prompt: str) -> str:
        system_prompt = """
            You are a Python developer.
            Your task is to write a Python code that solves the stated problem.
        """

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                stream=False,
                response_format={"type": "text"},
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in the response.")

            return content
        except Exception as e:
            print(f"Error generating code: {e}")
            raise e
