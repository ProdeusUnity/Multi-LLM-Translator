import os
from typing import Dict, Any
from openai import OpenAI

from api.base import BaseProvider
from utils.language_utils import get_language_code


class DeepseekProvider(BaseProvider):
    """Provider for Deepseek's API (OpenAI-compatible)."""
    
    def __init__(self):
        self.api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        self.base_url = "https://api.deepseek.com"
        self.client = None
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "Deepseek provides access to powerful AI models through an OpenAI-compatible API. "
            "To use this provider, you need an API key from Deepseek. "
            "You can sign up and get your API key at: https://platform.deepseek.com/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {}
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("DEEPSEEK_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for Deepseek."""
        self.api_key = api_key
        os.environ["DEEPSEEK_API_KEY"] = api_key
        self.client = None  # Reset client
    
    def _get_client(self):
        """Get or create a Deepseek client."""
        if not self.client and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self.client
    
    def test_connection(self) -> bool:
        """Test the Deepseek API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Make a simple call to test the connection
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"Deepseek connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using Deepseek."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for Deepseek")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Create system and user messages
            system_message = (
                f"You are a professional translator from {source_language} to {target_language}. "
                "Translate the following text accurately, preserving the meaning, tone, and style of the original. "
                "Only provide the translation, with no additional comments or explanations."
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text}
                ],
                temperature=0.3
            )
            
            # Extract the translation from the response
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
