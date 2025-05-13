from abc import ABC, abstractmethod
import os
from typing import Dict, Any, Optional, List

from utils.model_info import get_models_for_provider


class BaseProvider(ABC):
    """Base class for API providers."""
    
    @classmethod
    def get_name(cls) -> str:
        """Get the name of the provider."""
        return cls.__name__.replace("Provider", "")
    
    @classmethod
    def get_api_description(cls) -> str:
        """Get a description of the API and how to get API keys."""
        return "API provider with no description."
    
    @classmethod
    def get_additional_fields(cls) -> Dict[str, Dict[str, Any]]:
        """Get additional fields required for API configuration."""
        return {}
    
    @classmethod
    def get_models(cls) -> Dict[str, str]:
        """Get available models for this provider."""
        provider_name = cls.get_name()
        return get_models_for_provider(provider_name)
    
    @classmethod
    def is_api_key_set(cls) -> bool:
        """Check if the API key for this provider is set in the environment."""
        # Subclasses should override this
        return False
    
    @abstractmethod
    def set_api_key(self, api_key: str) -> None:
        """Set the API key for this provider."""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test the API connection."""
        pass
    
    @abstractmethod
    def translate(self, text: str, model: str, source_language: str, target_language: str) -> str:
        """Translate text using this provider."""
        pass


def get_provider_list() -> List[str]:
    """Get a list of all available providers."""
    return [
        "Anthropic",
        "Google AI Studio",
        "AI21",
        "OpenAI",
        "Deepseek",
        "Cohere",
        "Mistral",
        "Featherless",
        "ArliAI",
        "Openrouter",
        "OpenAI Compatible"
    ]


def get_provider_class(provider_name: str) -> type:
    """Get the provider class by name."""
    providers = {
        "Anthropic": AnthropicProvider,
        "Google AI Studio": GoogleAIStudioProvider,
        "AI21": AI21Provider,
        "OpenAI": OpenAIProvider,
        "Deepseek": DeepseekProvider,
        "Cohere": CohereProvider,
        "Mistral": MistralProvider,
        "Featherless": FeatherlessProvider,
        "ArliAI": ArliAIProvider,
        "Openrouter": OpenrouterProvider,
        "OpenAI Compatible": OAICompatibleProvider
    }
    
    return providers.get(provider_name, BaseProvider)


# Import specific providers (after defining the base class)
from api.anthropic import AnthropicProvider
from api.googleaistudio import GoogleAIStudioProvider
from api.ai21 import AI21Provider
from api.openai import OpenAIProvider
from api.deepseek import DeepseekProvider
from api.cohere import CohereProvider
from api.mistral import MistralProvider
from api.featherless import FeatherlessProvider
from api.arliai import ArliAIProvider
from api.openrouter import OpenrouterProvider
from api.oaicompat import OAICompatibleProvider
