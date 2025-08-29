from openai import OpenAI

from llm.api_base import APIBaseLLM

class OpenAILLM(APIBaseLLM):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, model: str, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=temperature
            )

            content = response.choices[0].message.content
            if content is None:
                raise Exception("No content found in response")
            return content
        except Exception as e:
            print(f"Error generating response: {e}")
            raise e