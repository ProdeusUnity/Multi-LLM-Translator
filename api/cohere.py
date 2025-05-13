import os
from typing import Dict, Any
import cohere

from api.base import BaseProvider
from utils.language_utils import get_language_code


class CohereProvider(BaseProvider):
    """Provider for Cohere's API."""
    
    def __init__(self):
        self.api_key = os.environ.get("COHERE_API_KEY", "")
        self.client = None
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "Cohere provides powerful language models like Command R, Command R+, and Aya Expanse. "
            "To use this provider, you need an API key from Cohere. "
            "You can sign up and get your API key at: https://dashboard.cohere.com/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {}
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("COHERE_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for Cohere."""
        self.api_key = api_key
        os.environ["COHERE_API_KEY"] = api_key
        self.client = None  # Reset client
    
    def _get_client(self):
        """Get or create a Cohere client."""
        if not self.client and self.api_key:
            self.client = cohere.Client(api_key=self.api_key)
        return self.client
    
    def test_connection(self) -> bool:
        """Test the Cohere API connection."""
        try:
            client = self._get_client()
            if not client:
                return False
            
            # Make a simple call to test the connection
            response = client.chat(
                model="command-r",
                message="Hello"
            )
            return True
        except Exception as e:
            print(f"Cohere connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using Cohere."""
        client = self._get_client()
        if not client:
            raise ValueError("API key not set for Cohere")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Create translation prompt
            prompt = (
                f"Translate the following {source_language} text to {target_language}. "
                "Provide only the translation without any additional text, comments, or explanations.\n\n"
                f"Text to translate: {text}"
            )
            
            # Create chat history with system message
            chat_history = [
                {"role": "SYSTEM", "message": "You are a professional translator. Your task is to translate text accurately while preserving the meaning, tone, and style."}
            ]
            
            response = client.chat(
                model=model,
                message=prompt,
                chat_history=chat_history,
                temperature=0.3
            )
            
            # Extract the translation from the response
            return response.text
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")