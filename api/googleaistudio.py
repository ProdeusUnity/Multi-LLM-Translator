import os
from typing import Dict, Any
import google.generativeai as genai
from google.generativeai import types

from api.base import BaseProvider
from utils.language_utils import get_language_code


class GoogleAIStudioProvider(BaseProvider):
    """Provider for Google's AI Studio API."""
    
    def __init__(self):
        self.api_key = os.environ.get("GOOGLE_API_KEY", "")
        self.client = None
    
    @classmethod
    def get_name(cls) -> str:
        """Override to return the exact name as expected in model_info.py"""
        return "Google AI Studio"
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "Google's AI Studio API provides access to advanced AI models. "
            "To use this provider, you need an API key from Google AI Studio. "
            "You can sign up and get your API key at: https://aistudio.google.com/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {}
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("GOOGLE_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for Google AI Studio."""
        self.api_key = api_key
        os.environ["GOOGLE_API_KEY"] = api_key
        
        # Configure the Google AI Studio client
        if api_key:
            genai.configure(api_key=api_key)
            self.client = genai
        else:
            self.client = None
    
    def _get_client(self):
        """Get or create a Google client."""
        if not self.client and self.api_key:
            genai.configure(api_key=self.api_key)
            self.client = genai
        return self.client
    
    def test_connection(self) -> bool:
        """Test the Google AI Studio API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Get models to test connection
            models = client.list_models()
            return len(list(models)) > 0
        except Exception as e:
            print(f"AI Studio connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using Google AI Studio."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for Google AI Studio")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Create model instance
            model_instance = client.GenerativeModel(model)
            
            # Create translation prompt
            prompt = (
                f"Translate the following {source_language} text into {target_language}.\n\n"
                f"Text to translate: {text}\n\n"
                "Only provide the translation, with no additional comments or explanations."
            )
            
            # Generate content
            response = model_instance.generate_content(prompt)
            
            # Extract and return the translation
            if hasattr(response, 'text'):
                return response.text
            elif hasattr(response, 'parts'):
                return response.parts[0].text
            else:
                # Extract from other response formats if needed
                return str(response)
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")