import os
from openai import OpenAI
from typing import Dict, Any

from api.base import BaseProvider
from utils.language_utils import get_language_code


class OpenAIProvider(BaseProvider):
    """Provider for OpenAI's API."""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.client = None
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "OpenAI's API provides access to GPT models like GPT-4o. "
            "To use this provider, you need an API key from OpenAI. "
            "You can sign up and get your API key at: https://platform.openai.com/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "organization_id": {
                "label": "Organization ID (optional)",
                "password": False
            }
        }
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("OPENAI_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for OpenAI."""
        self.api_key = api_key
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = None  # Reset client
    
    def set_organization_id(self, organization_id: str) -> None:
        """Set the organization ID for OpenAI."""
        if organization_id:
            os.environ["OPENAI_ORGANIZATION"] = organization_id
        elif "OPENAI_ORGANIZATION" in os.environ:
            del os.environ["OPENAI_ORGANIZATION"]
        self.client = None  # Reset client
    
    def _get_client(self):
        """Get or create an OpenAI client."""
        if not self.client and self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        return self.client
    
    def test_connection(self) -> bool:
        """Test the OpenAI API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Make a simple call to test the connection
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            return True
        except Exception as e:
            print(f"OpenAI connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using OpenAI."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for OpenAI")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Use system prompt for better translation
            system_prompt = (
                f"You are a professional translator from {source_language} to {target_language}. "
                "Translate the following text accurately, preserving the meaning, tone, and style of the original. "
                "Only provide the translation, with no additional comments or explanations."
            )
            
            response = client.chat.completions.create(
                model=model,
                temperature=0.3,  # Lower temperature for more precise translation
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            
            # Extract the translation from the response
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
