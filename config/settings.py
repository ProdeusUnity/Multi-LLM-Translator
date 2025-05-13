import os
import json
from utils.encryption import encrypt_data, decrypt_data


class AppSettings:
    """Manage application settings and API keys."""
    
    def __init__(self):
        # Define paths
        self.app_dir = os.path.join(os.path.expanduser("~"), ".translator_app")
        self.settings_file = os.path.join(self.app_dir, "settings.json")
        self.api_keys_file = os.path.join(self.app_dir, "api_keys.enc")
        
        # Create directory if it doesn't exist
        os.makedirs(self.app_dir, exist_ok=True)
        
        # Default settings
        self.settings = {
            "theme": "dark",
            "provider": "Anthropic",
            "source_language": "English",
            "target_language": "Spanish",
            "models": {}  # Store last used model for each provider
        }
        
        # API keys (encrypted)
        self.api_keys = {}
        
        # Load settings
        self.load()
    
    def load(self):
        """Load settings from disk."""
        # Load general settings
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings.update(loaded_settings)
            except Exception as e:
                print(f"Error loading settings: {str(e)}")
        
        # Load API keys
        if os.path.exists(self.api_keys_file):
            try:
                with open(self.api_keys_file, 'rb') as f:
                    encrypted_data = f.read()
                    if encrypted_data:
                        decrypted_data = decrypt_data(encrypted_data)
                        self.api_keys = json.loads(decrypted_data)
            except Exception as e:
                print(f"Error loading API keys: {str(e)}")
    
    def save(self):
        """Save settings to disk."""
        # Save general settings
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")
        
        # Save API keys (encrypted)
        if self.api_keys:
            try:
                encrypted_data = encrypt_data(json.dumps(self.api_keys))
                with open(self.api_keys_file, 'wb') as f:
                    f.write(encrypted_data)
            except Exception as e:
                print(f"Error saving API keys: {str(e)}")
    
    # Theme settings
    def get_theme(self):
        """Get the current theme."""
        return self.settings.get("theme", "dark")
    
    def set_theme(self, theme):
        """Set the application theme."""
        self.settings["theme"] = theme
    
    # Provider settings
    def get_provider(self):
        """Get the current provider."""
        return self.settings.get("provider", "Anthropic")
    
    def set_provider(self, provider):
        """Set the current provider."""
        self.settings["provider"] = provider
    
    # Model settings
    def get_model(self, provider):
        """Get the last used model for a provider."""
        return self.settings.get("models", {}).get(provider, "")
    
    def set_model(self, provider, model):
        """Set the model for a provider."""
        if "models" not in self.settings:
            self.settings["models"] = {}
        self.settings["models"][provider] = model
    
    # Language settings
    def get_source_language(self):
        """Get the source language."""
        return self.settings.get("source_language", "English")
    
    def set_source_language(self, language):
        """Set the source language."""
        self.settings["source_language"] = language
    
    def get_target_language(self):
        """Get the target language."""
        return self.settings.get("target_language", "Spanish")
    
    def set_target_language(self, language):
        """Set the target language."""
        self.settings["target_language"] = language
    
    # API key management
    def get_api_key(self, provider):
        """Get the API key for a provider."""
        provider_data = self.api_keys.get(provider, {})
        return provider_data.get("api_key", "")
    
    def set_api_key(self, provider, api_key):
        """Set the API key for a provider."""
        if provider not in self.api_keys:
            self.api_keys[provider] = {}
        self.api_keys[provider]["api_key"] = api_key
    
    def get_api_field(self, provider, field_name):
        """Get an additional API field for a provider."""
        provider_data = self.api_keys.get(provider, {})
        return provider_data.get(field_name, "")
    
    def set_api_field(self, provider, field_name, value):
        """Set an additional API field for a provider."""
        if provider not in self.api_keys:
            self.api_keys[provider] = {}
        self.api_keys[provider][field_name] = value
