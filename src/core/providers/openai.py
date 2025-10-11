from openai import OpenAI

from core.providers._base import ProviderBase
from core.models import Provider

class OpenAIProvider(ProviderBase):
    def __init__(self, provider_config: dict):
        self.name = Provider.OPENAI
        self.client = OpenAI(api_key = provider_config.get("api-key"))
        self.model = provider_config.get("model")

    def generate_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0, top_p: float = 1.0) -> str:
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream = False,
                response_format = { "type": "text" },
                temperature = temperature,
                top_p = top_p,
            )

            # Robust response validation
            if not response.choices:
                raise Exception("No response from OpenAI API")
            
            content = response.choices[0].message.content
            
            if content is None:
                raise Exception("No content in response from OpenAI API")
            
            if not content.strip():
                raise Exception("Empty content in response from OpenAI API")
            
            # Basic content cleanup
            content = content.strip()
            return content
        except Exception as e:
            raise Exception(f"Error generating response from OpenAI API: {e}")