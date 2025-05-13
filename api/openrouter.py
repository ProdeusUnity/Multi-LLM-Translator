import os
from typing import Dict, Any
from openai import OpenAI

from api.base import BaseProvider
from utils.language_utils import get_language_code


class OpenrouterProvider(BaseProvider):
    """Provider for Openrouter's API (routing to various models)."""
    
    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY", "")
        self.app_name = os.environ.get("OPENROUTER_APP_NAME", "AI Translator")
        self.site_url = os.environ.get("OPENROUTER_SITE_URL", "http://localhost")
        self.base_url = "https://openrouter.ai/api/v1"
        self.client = None
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "Openrouter provides access to various AI models from different providers through a unified API. "
            "To use this provider, you need an API key from Openrouter. "
            "You can sign up and get your API key at: https://openrouter.ai/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "app_name": {
                "label": "Application Name",
                "password": False
            },
            "site_url": {
                "label": "Site URL",
                "password": False
            }
        }
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("OPENROUTER_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for Openrouter."""
        self.api_key = api_key
        os.environ["OPENROUTER_API_KEY"] = api_key
        self.client = None  # Reset client
    
    def set_app_name(self, app_name: str) -> None:
        """Set the application name for Openrouter."""
        self.app_name = app_name
        os.environ["OPENROUTER_APP_NAME"] = app_name
        self.client = None  # Reset client
    
    def set_site_url(self, site_url: str) -> None:
        """Set the site URL for Openrouter."""
        self.site_url = site_url
        os.environ["OPENROUTER_SITE_URL"] = site_url
        self.client = None  # Reset client
    
    def _get_client(self):
        """Get or create an Openrouter client."""
        if not self.client and self.api_key:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
        return self.client

    def test_connection(self) -> bool:
        """Test the Openrouter API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Make a simple call to test the connection
            response = client.chat.completions.create(
                model="google/gemma-3-27b-it:free",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                max_tokens=5,
                extra_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.app_name,
                }
            )
            return True
        except Exception as e:
            print(f"Openrouter connection error: {str(e)}")
            return False

    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using Openrouter."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for Openrouter")
        
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
                temperature=0.3,
                extra_headers={
                    "HTTP-Referer": self.site_url,
                    "X-Title": self.app_name,
                }
            )
            
            # Extract the translation from the response
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
