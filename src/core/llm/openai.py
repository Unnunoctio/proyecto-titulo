from openai import OpenAI

from core.llm.api_base import APIBaseLLM

class OpenAILLM(APIBaseLLM):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key)
    
    def generate(self, model: str, system_prompt: str, user_prompt: str, temperature: float = 0.0, top_p: float = 1.0) -> str:
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=False,
                response_format={"type": "text"},
                temperature=temperature,
                top_p=top_p,
            )

            # Robust response validation
            if not response.choices:
                raise Exception("No response choices received from API")
            
            content = response.choices[0].message.content
            if content is None:
                raise Exception("Response content is None")
                
            if not content.strip():
                raise Exception("Response content is empty")

            # Basic content cleanup
            content = content.strip()
            return content
        except Exception as e:
            print(f"Error generating response: {e}")
            raise e