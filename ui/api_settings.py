from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QTabWidget, QWidget,
    QFormLayout, QDialogButtonBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot

from api.base import get_provider_list, get_provider_class


class ApiKeyInput(QWidget):
    """Widget for entering and saving API keys for a specific provider."""
    
    def __init__(self, provider_name, settings, parent=None):
        super().__init__(parent)
        self.provider_name = provider_name
        self.settings = settings
        self.provider_class = get_provider_class(provider_name)
        
        self.setup_ui()
        self.load_api_key()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Description
        description = self.provider_class.get_api_description()
        description_label = QLabel(description)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)
        
        # Form layout for API key
        form_layout = QFormLayout()
        
        # API key input
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("API Key:", self.api_key_input)
        
        # Additional fields if needed
        additional_fields = self.provider_class.get_additional_fields()
        self.additional_inputs = {}
        
        for field_name, field_info in additional_fields.items():
            input_widget = QLineEdit()
            if field_info.get("password", False):
                input_widget.setEchoMode(QLineEdit.Password)
            
            form_layout.addRow(f"{field_info['label']}:", input_widget)
            self.additional_inputs[field_name] = input_widget
        
        layout.addLayout(form_layout)
        
        # Test connection button
        self.test_button = QPushButton("Test Connection")
        self.test_button.clicked.connect(self.test_connection)
        layout.addWidget(self.test_button)
        
        # Add stretch to push everything to the top
        layout.addStretch(1)
    
    def load_api_key(self):
        """Load saved API key from settings."""
        api_key = self.settings.get_api_key(self.provider_name)
        if api_key:
            self.api_key_input.setText(api_key)
        
        # Load additional fields
        for field_name in self.additional_inputs.keys():
            value = self.settings.get_api_field(self.provider_name, field_name)
            if value:
                self.additional_inputs[field_name].setText(value)
    
    def save_api_key(self):
        """Save API key to settings."""
        api_key = self.api_key_input.text().strip()
        self.settings.set_api_key(self.provider_name, api_key)
        
        # Save additional fields
        for field_name, input_widget in self.additional_inputs.items():
            value = input_widget.text().strip()
            self.settings.set_api_field(self.provider_name, field_name, value)
        
        # Ensure settings are saved immediately
        self.settings.save()
    
    def get_api_key(self):
        """Get the current API key (from input or settings)."""
        # First try the input field
        api_key = self.api_key_input.text().strip()
        if not api_key:
            # If empty, try to get from settings
            api_key = self.settings.get_api_key(self.provider_name)
            if api_key:
                self.api_key_input.setText(api_key)
        return api_key
    
    def get_additional_field(self, field_name):
        """Get an additional field value (from input or settings)."""
        input_widget = self.additional_inputs.get(field_name)
        if not input_widget:
            return None
            
        # First try the input field
        value = input_widget.text().strip()
        if not value:
            # If empty, try to get from settings
            value = self.settings.get_api_field(self.provider_name, field_name)
            if value:
                input_widget.setText(value)
        return value
    
    def has_valid_api_key(self):
        """Check if this provider has a valid API key."""
        # Check for API key
        api_key = self.get_api_key()
        if not api_key:
            return False
        
        # Check additional required fields
        for field_name in self.additional_inputs.keys():
            value = self.get_additional_field(field_name)
            if not value:
                return False
        
        return True
    
    @Slot()
    def test_connection(self):
        """Test the API connection with the provided key."""
        api_key = self.get_api_key()
        if not api_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter an API key to test.")
            return
        
        # Collect additional fields
        additional_fields = {}
        for field_name in self.additional_inputs.keys():
            additional_fields[field_name] = self.get_additional_field(field_name)
            if not additional_fields[field_name]:
                QMessageBox.warning(self, "Missing Field", f"Please enter a value for {field_name}.")
                return
        
        try:
            # Create provider instance
            provider = self.provider_class()
            provider.set_api_key(api_key)
            
            # Set additional fields
            for field_name, value in additional_fields.items():
                if hasattr(provider, f"set_{field_name}"):
                    getattr(provider, f"set_{field_name}")(value)
            
            # Test connection
            result = provider.test_connection()
            
            if result:
                QMessageBox.information(
                    self, "Connection Successful", 
                    f"Successfully connected to {self.provider_name} API."
                )
                # Save the working API key
                self.save_api_key()
            else:
                QMessageBox.critical(
                    self, "Connection Failed", 
                    f"Failed to connect to {self.provider_name} API. Please check your API key."
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", 
                f"Error testing connection: {str(e)}"
            )


class ApiSettingsDialog(QDialog):
    """Dialog for managing API keys for all providers."""
    
    api_keys_updated = Signal()
    
    def __init__(self, settings, parent=None, force_show=False):
        super().__init__(parent)
        self.settings = settings
        self.force_show = force_show
        self.setup_ui()
        
        # If not forcing the dialog to show, check if we have valid API keys
        if not force_show:
            # Force settings to load from disk first
            self.settings.load()
            
            if self.has_valid_api_keys():
                # We have valid keys, no need to show the dialog
                self.accept()
                return
    
    def has_valid_api_keys(self):
        """Check if at least one provider has a valid API key."""
        # Debug output to help diagnose the issue
        print("Checking for valid API keys...")
        
        for provider in get_provider_list():
            provider_class = get_provider_class(provider)
            api_key = self.settings.get_api_key(provider)
            
            print(f"Provider: {provider}, API Key exists: {bool(api_key)}")
            
            # If no API key, this provider isn't valid
            if not api_key:
                continue
                
            # Check additional fields if needed
            additional_fields = provider_class.get_additional_fields()
            all_fields_valid = True
            
            for field_name in additional_fields.keys():
                field_value = self.settings.get_api_field(provider, field_name)
                print(f"  Field: {field_name}, Value exists: {bool(field_value)}")
                if not field_value:
                    all_fields_valid = False
                    break
            
            # If this provider has a valid API key and all required fields, we're good
            if all_fields_valid:
                print(f"Provider {provider} has valid API key and all required fields")
                return True
        
        print("No valid API keys found")
        return False
    
    def setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("API Settings")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "Enter your API keys for the providers you want to use. "
            "The keys will be stored securely on your device."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Tab widget for providers
        self.tab_widget = QTabWidget()
        providers = get_provider_list()
        self.provider_widgets = {}
        
        for provider in providers:
            provider_widget = ApiKeyInput(provider, self.settings)
            self.tab_widget.addTab(provider_widget, provider)
            self.provider_widgets[provider] = provider_widget
        
        layout.addWidget(self.tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def accept(self):
        """Save all API keys when the dialog is accepted."""
        for provider, widget in self.provider_widgets.items():
            widget.save_api_key()
        
        # Ensure settings are saved
        self.settings.save()
        self.api_keys_updated.emit()
        super().accept()