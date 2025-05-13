import os
import requests
import json
from typing import Dict, Any

from api.base import BaseProvider
from utils.language_utils import get_language_code


class ArliAIProvider(BaseProvider):
    """Provider for ArliAI's API."""
    
    def __init__(self):
        self.api_key = os.environ.get("ARLIAI_API_KEY", "")
        self.api_url = "https://api.arliai.com/v1/chat/completions"
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "ArliAI provides access to various AI models including Mistral variants. "
            "To use this provider, you need an API key from ArliAI. "
            "You can sign up and get your API key at: https://arliai.com/"
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {}
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        return bool(os.environ.get("ARLIAI_API_KEY", ""))
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for ArliAI."""
        self.api_key = api_key
        os.environ["ARLIAI_API_KEY"] = api_key
    
    def test_connection(self) -> bool:
        """Test the ArliAI API connection."""
        try:
            if not self.api_key:
                return False
            
            # Prepare headers and payload for a simple test request
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.api_key}"
            }
            
            payload = json.dumps({
                "model": "Mistral-Nemo-12B-Instruct-2407",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello"}
                ],
                "temperature": 0.7,
                "max_tokens": 10,
                "stream": False,
                "multipler": 2
            })
            
            # Send test request
            response = requests.post(self.api_url, headers=headers, data=payload)
            
            # Check if the request was successful
            return response.status_code == 200
        except Exception as e:
            print(f"ArliAI connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using ArliAI."""
        if not self.api_key:
            raise ValueError("API key not set for ArliAI")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Prepare headers
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.api_key}"
            }
            
            # Create system message for translation
            system_message = (
                f"You are a professional translator from {source_language} to {target_language}. "
                "Translate the following text accurately, preserving the meaning, tone, and style of the original. "
                "Only provide the translation, with no additional comments or explanations."
            )
            
            # Prepare payload
            payload = json.dumps({
                "model": model,
                "messages": [
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text}
                ],
                "temperature": 0.3,
                "top_p": 0.9,
                "max_tokens": 2048,
                "stream": False
            })
            
            # Send request
            response = requests.post(self.api_url, headers=headers, data=payload)
            
            # Check if the request was successful
            if response.status_code == 200:
                json_response = response.json()
                return json_response['choices'][0]['message']['content']
            else:
                raise Exception(f"Error from ArliAI API: Status code {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")
