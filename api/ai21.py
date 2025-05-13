import os
from typing import Dict, Any
from ai21 import AI21Client
from ai21.models.chat import ChatMessage

from api.base import BaseProvider
from utils.language_utils import get_language_code


class AI21Provider(BaseProvider):
    """Provider for AI21's Jamba API."""
    
    def __init__(self):
        self.api_key = os.environ.get("AI21_API_KEY", "")
        self.client = None
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "AI21's API provides access to Jamba models. "
            "To use this provider, you need an API key from AI21. "
            "You can sign up and get your API key at: https://studio.ai21.com/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {}
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("AI21_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for AI21."""
        self.api_key = api_key
        os.environ["AI21_API_KEY"] = api_key
        self.client = None  # Reset client
    
    def _get_client(self):
        """Get or create an AI21 client."""
        if not self.client and self.api_key:
            self.client = AI21Client(api_key=self.api_key)
        return self.client
    
    def test_connection(self) -> bool:
        """Test the AI21 API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Make a simple call to test the connection
            response = client.chat.completions.create(
                model="jamba-1.5-mini",
                messages=[
                    ChatMessage(
                        role="user",
                        content="Hello",
                    )
                ],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"AI21 connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using AI21 (Jamba)."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for AI21")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Create system and user messages
            system_message = (
                f"You are a professional translator from {source_language} to {target_language}. "
                "Translate the provided text accurately, preserving meaning, tone, and style. "
                "Only provide the translation without additional comments."
            )
            
            response = client.chat.completions.create(
                model=model,
                messages=[
                    ChatMessage(role="system", content=system_message),
                    ChatMessage(role="user", content=text),
                ],
                temperature=0.3,
                max_tokens=2048,
            )
            
            # Extract the translation from the response
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
