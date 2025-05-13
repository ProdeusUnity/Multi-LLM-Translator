import os
import json
import requests
from typing import Dict, Any, List, Optional

from api.base import BaseProvider
from utils.language_utils import get_language_code
from utils.model_info import get_model_display_name as get_display_name


class OAICompatibleProvider(BaseProvider):
    """Provider for OpenAI-compatible APIs like KoboldAI, LMStudio, etc."""
    
    def __init__(self):
        self.api_url = os.environ.get("KOBOLD_API_URL", "http://127.0.0.1:5001")
        self.api_key = os.environ.get("KOBOLD_API_KEY", "")
        self.available_models = []
    
    @classmethod
    def get_api_description(cls) -> str:
        return (
            "Custom (OAI Compatible) provider for OpenAI-compatible APIs like KoboldAI, KoboldCpp, etc. "
            "To use this provider, you need to have an OpenAI-compatible API running on your machine or a remote server. "
            "Enter the full URL including http:// and port, e.g., http://127.0.0.1:5001. "
            "Some providers require an API key, which you can enter if needed."
        )
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "api_url": {
                "label": "API URL",
                "password": False
            },
            "api_key": {
                "label": "API Key (optional)",
                "password": True
            }
        }
    
    @classmethod
    def get_model_display_name(cls, model_id):
        """Get a user-friendly display name for a model."""
        from utils.model_info import get_model_display_name
        return get_model_display_name("OpenAI Compatible", model_id)

    @classmethod
    def is_api_key_set(cls) -> bool:
        # This provider needs at least a URL
        api_url = os.environ.get("KOBOLD_API_URL", "")
        return bool(api_url)
    
    def set_api_key(self, api_key: str) -> None:
        """Set the API key if the provider requires it."""
        self.api_key = api_key
        os.environ["KOBOLD_API_KEY"] = api_key
    
    def set_api_url(self, api_url: str) -> None:
        """Set the API URL."""
        self.api_url = api_url
        os.environ["KOBOLD_API_URL"] = api_url
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests, including API key if available."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def _fetch_available_models(self) -> List[Dict[str, Any]]:
        """Fetch available models from the API."""
        try:
            url = f"{self.api_url}/v1/models"
            response = requests.get(url, headers=self._get_headers())
            
            if response.status_code == 200:
                data = response.json()
                if "data" in data:  # OpenAI format
                    return data["data"]
                elif "result" in data:  # Some Kobold implementations
                    return data["result"]
                return []
            return []
        except Exception as e:
            print(f"Error fetching models: {str(e)}")
            return []
    
    def _get_model_id(self, model_name: Optional[str] = None) -> str:
        """Get the actual model ID to use with the API."""
        if not self.available_models:
            self.available_models = self._fetch_available_models()
        
        # If no models found or no specific model requested, return default
        if not self.available_models:
            return "default"
        
        # If a specific model was requested, try to find it
        if model_name:
            for model in self.available_models:
                if model.get("id") == model_name or model.get("name") == model_name:
                    return model.get("id")
        
        # Otherwise return the first available model
        return self.available_models[0].get("id", "default")
    
    def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            if not self.api_url:
                return False
            
            # Try to get model information
            models = self._fetch_available_models()
            return len(models) > 0
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False
    
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using the OpenAI-compatible API."""
        if not self.api_url:
            raise ValueError("API URL not set")
        
        source_code = get_language_code(source_language)
        target_code = get_language_code(target_language)
        
        try:
            # Get the actual model ID to use
            model_id = self._get_model_id(model)
            
            # Create a translation prompt
            prompt = (
                f"### Instruction:\n"
                f"Translate the following {source_language} text to {target_language}. "
                "Only provide the translation, with no additional comments or explanations.\n\n"
                f"### Input:\n{text}\n\n"
                "### Response:"
            )
            
            # Prepare the request using OpenAI-compatible format
            payload = {
                "model": model_id,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1024,
                "top_p": 0.9,
                "stop": ["###"]
            }
            
            # Send the request with headers that may include the API key
            url = f"{self.api_url}/v1/chat/completions"
            response = requests.post(url, json=payload, headers=self._get_headers())
            
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # Extract the generated text
                if "choices" in data and len(data["choices"]) > 0:
                    generated_text = data["choices"][0]["message"]["content"]
                    return generated_text.strip()
                else:
                    raise Exception("No response content received")
            else:
                # If chat completions fails, try the legacy completions endpoint
                payload = {
                    "model": model_id,
                    "prompt": prompt,
                    "temperature": 0.7,
                    "max_tokens": 1024,
                    "top_p": 0.9,
                    "stop": ["###"]
                }
                
                url = f"{self.api_url}/v1/completions"
                response = requests.post(url, json=payload, headers=self._get_headers())
                
                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        generated_text = data["choices"][0]["text"]
                        return generated_text.strip()
                
                raise Exception(f"Error from API: Status code {response.status_code}, {response.text}")
        except Exception as e:
            raise Exception(f"Translation error: {str(e)}")