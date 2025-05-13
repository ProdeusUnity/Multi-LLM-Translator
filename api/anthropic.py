import os
import anthropic
from typing import Dict, Any

from api.base import BaseProvider
from utils.language_utils import get_language_code


class AnthropicProvider(BaseProvider):
    """Provider for Anthropic's Claude API."""
    
    def __init__(self):
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = None
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "Anthropic's Claude API provides access to Claude, a state-of-the-art AI assistant. "
            "To use this provider, you need an API key from Anthropic. "
            "You can sign up and get your API key at: https://console.anthropic.com/ "
            "Note: DO NOT SHARE API KEYS!! Leaking an API key can rack up huge bills, I don't want that for you, okay? :D"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {}
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("ANTHROPIC_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for Anthropic."""
        self.api_key = api_key
        os.environ["ANTHROPIC_API_KEY"] = api_key
        self.client = None  # Reset client to create a new one with the updated key
    
    def _get_client(self):
        """Get or create an Anthropic client."""
        if not self.client and self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        return self.client
    
    def test_connection(self) -> bool:
        """Test the Anthropic API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Make a simple call to test the connection
            response = client.messages.create(
                model="claude-3-5-sonnet-20240620",
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}]
            )
            return True
        except Exception as e:
            print(f"Anthropic connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using Claude."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for Anthropic")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        # Use of system prompt for better translation quality
        system_prompt = (
            f"You are a professional translator from {source_language} to {target_language}. "
            "Translate the following text accurately, preserving the meaning, tone, and style of the original. "
            "Only provide the translation, with no additional comments or explanations."
        )
        
        try:
            response = client.messages.create(
                model=model,
                system=system_prompt,
                max_tokens=4000,
                messages=[
                    {"role": "user", "content": text}
                ]
            )
            
            # Extract the translation from the response
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
