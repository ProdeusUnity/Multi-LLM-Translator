from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QComboBox, QTextEdit, QPushButton, QLabel, 
    QStatusBar, QToolBar, QDialog, QTabWidget,
    QSplitter, QFrame, QMenu, QMessageBox,QApplication
)
from PySide6.QtCore import Qt, QSize, Signal, Slot, QThread
from PySide6.QtGui import QAction, QIcon, QKeySequence, QTextCursor

from ui.api_settings import ApiSettingsDialog
from ui.theme_manager import ThemeSettingsDialog
from api.base import get_provider_list, get_provider_class
from utils.language_utils import get_language_list, get_language_name, get_language_code


class TranslationWorker(QThread):
    """Worker thread for running translations without blocking the UI."""
    finished = Signal(str, bool)  # Result, success/failure
    
    def __init__(self, provider, model, source_text, source_lang, target_lang):
        super().__init__()
        self.provider = provider
        self.model = model
        self.source_text = source_text
        self.source_lang = source_lang
        self.target_lang = target_lang
        
    def run(self):
        try:
            api_instance = get_provider_class(self.provider)()
            result = api_instance.translate(
                text=self.source_text,
                model=self.model,
                source_language=self.source_lang,
                target_language=self.target_lang
            )
            self.finished.emit(result, True)
        except Exception as e:
            self.finished.emit(str(e), False)


class MainWindow(QMainWindow):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.translation_worker = None
        
        # Set up the UI
        self.setup_ui()
        
        # Load saved settings
        self.load_settings()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("AI Translator")
        self.setMinimumSize(1000, 700)
        
        # Create central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Create toolbar
        self.setup_toolbar()
        
        # Create provider and model selection area
        self.setup_provider_selection()
        
        # Create language selection area
        self.setup_language_selection()
        
        # Create translation area
        self.setup_translation_area()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready")
        
    def setup_toolbar(self):
        """Set up the application toolbar."""
        self.toolbar = QToolBar("Main Toolbar")
        self.toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(self.toolbar)
        
        # API Settings action
        self.api_settings_action = QAction(QIcon.fromTheme("preferences-system"), "API Settings", self)
        self.api_settings_action.triggered.connect(self.show_api_settings)
        self.toolbar.addAction(self.api_settings_action)
        
        # Theme Settings action
        self.theme_settings_action = QAction(QIcon.fromTheme("preferences-desktop-theme"), "Theme Settings", self)
        self.theme_settings_action.triggered.connect(self.show_theme_settings)
        self.toolbar.addAction(self.theme_settings_action)
        
        # Add separator
        self.toolbar.addSeparator()
        
        # Swap languages action
        self.swap_languages_action = QAction(QIcon.fromTheme("object-flip-horizontal"), "Swap Languages", self)
        self.swap_languages_action.triggered.connect(self.swap_languages)
        self.toolbar.addAction(self.swap_languages_action)
        
    def setup_provider_selection(self):
        """Set up the provider and model selection UI elements."""
        provider_frame = QFrame()
        provider_layout = QHBoxLayout(provider_frame)
        
        # Provider selection
        provider_layout.addWidget(QLabel("AI Provider:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(get_provider_list())
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        provider_layout.addWidget(self.provider_combo)
        
        # Model selection
        provider_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.setEditable(True)
        self.model_combo.setMinimumWidth(300)
        provider_layout.addWidget(self.model_combo)
        
        # Add to main layout
        self.main_layout.addWidget(provider_frame)
        
    def setup_language_selection(self):
        """Set up the language selection UI elements."""
        language_frame = QFrame()
        language_layout = QHBoxLayout(language_frame)
        
        # Source language selection
        language_layout.addWidget(QLabel("From:"))
        self.source_language_combo = QComboBox()
        self.source_language_combo.addItems(get_language_list())
        language_layout.addWidget(self.source_language_combo)
        
        # Target language selection
        language_layout.addWidget(QLabel("To:"))
        self.target_language_combo = QComboBox()
        self.target_language_combo.addItems(get_language_list())
        language_layout.addWidget(self.target_language_combo)
        
        # Add to main layout
        self.main_layout.addWidget(language_frame)
        
    def setup_translation_area(self):
        """Set up the translation text areas."""
        # Create splitter for text areas
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Source text area
        self.source_text_frame = QFrame()
        source_layout = QVBoxLayout(self.source_text_frame)
        source_layout.addWidget(QLabel("Source Text:"))
        self.source_text = QTextEdit()
        source_layout.addWidget(self.source_text)
        
        # Create translate button
        self.translate_button = QPushButton("Translate")
        self.translate_button.clicked.connect(self.translate_text)
        source_layout.addWidget(self.translate_button)
        
        # Target text area
        self.target_text_frame = QFrame()
        target_layout = QVBoxLayout(self.target_text_frame)
        target_layout.addWidget(QLabel("Translation:"))
        self.target_text = QTextEdit()
        self.target_text.setReadOnly(True)
        target_layout.addWidget(self.target_text)
        
        # Create copy button
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_translation)
        target_layout.addWidget(self.copy_button)
        
        # Add frames to splitter
        self.splitter.addWidget(self.source_text_frame)
        self.splitter.addWidget(self.target_text_frame)
        
        # Add splitter to main layout
        self.main_layout.addWidget(self.splitter, 1)  # Give it stretch factor
        
    def load_settings(self):
        """Load saved settings from the settings manager."""
        # Set the provider
        saved_provider = self.settings.get_provider()
        if saved_provider:
            index = self.provider_combo.findText(saved_provider)
            if index >= 0:
                self.provider_combo.setCurrentIndex(index)
                
        # Set source and target languages
        source_lang = self.settings.get_source_language()
        if source_lang:
            index = self.source_language_combo.findText(source_lang)
            if index >= 0:
                self.source_language_combo.setCurrentIndex(index)
                
        target_lang = self.settings.get_target_language()
        if target_lang:
            index = self.target_language_combo.findText(target_lang)
            if index >= 0:
                self.target_language_combo.setCurrentIndex(index)
    
        # Populate models for the current provider
        self.populate_models()
        
        # Set the model if saved
        provider = self.provider_combo.currentText()
        saved_model = self.settings.get_model(provider)
        if saved_model:
            # Find the model in the combobox by its model ID (saved in itemData)
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == saved_model:
                    self.model_combo.setCurrentIndex(i)
                    break
            else:
                # If model not found in the predefined list, add it as a custom model
                provider_class = get_provider_class(provider)
                display_name = provider_class.get_model_display_name(saved_model)
                self.model_combo.addItem(display_name, saved_model)
                self.model_combo.setCurrentIndex(self.model_combo.count() - 1)
    
    def save_current_settings(self):
        """Save current UI settings."""
        provider = self.provider_combo.currentText()
        self.settings.set_provider(provider)
        
        # Get the model ID from the item data rather than the display text
        model_index = self.model_combo.currentIndex()
        if model_index >= 0:
            model = self.model_combo.itemData(model_index)
        else:
            # Fallback to text if no item data (for custom models)
            model = self.model_combo.currentText()
            
        self.settings.set_model(provider, model)
        
        source_lang = self.source_language_combo.currentText()
        self.settings.set_source_language(source_lang)
        
        target_lang = self.target_language_combo.currentText()
        self.settings.set_target_language(target_lang)
        
        self.settings.save()
    
    @Slot()
    def on_provider_changed(self):
        """Handle provider change event."""
        # Populate models for the selected provider
        self.populate_models()
    
    def populate_models(self):
        """Populate the model selection combobox based on the selected provider."""
        provider = self.provider_combo.currentText()
        
        # Clear current models
        self.model_combo.clear()
        
        try:
            # Get the provider class
            provider_class = get_provider_class(provider)
            
            # Get models from the provider
            models = provider_class.get_models()
            
            # Add models to combobox - use the model name as display text and model_id as data
            for display_name, model_id in models.items():
                self.model_combo.addItem(display_name, model_id)
                
        except Exception as e:
            self.statusBar.showMessage(f"Error loading models: {str(e)}", 5000)
    
    @Slot()
    def show_api_settings(self):
        """Show the API settings dialog."""
        dialog = ApiSettingsDialog(self.settings, self)
        if dialog.exec():
            # Reload models after settings change
            self.populate_models()
    
    @Slot()
    def show_theme_settings(self):
        """Show the theme settings dialog."""
        dialog = ThemeSettingsDialog(self.settings, self)
        if dialog.exec():
            # Apply theme changes
            QMessageBox.information(
                self, 
                "Theme Changed", 
                "Please restart the application for theme changes to take effect."
            )
    
    @Slot()
    def swap_languages(self):
        """Swap source and target languages."""
        source_index = self.source_language_combo.currentIndex()
        target_index = self.target_language_combo.currentIndex()
        
        self.source_language_combo.setCurrentIndex(target_index)
        self.target_language_combo.setCurrentIndex(source_index)
        
        # Also swap text if there's content in both fields
        source_text = self.source_text.toPlainText()
        target_text = self.target_text.toPlainText()
        
        if source_text and target_text:
            self.source_text.setPlainText(target_text)
            self.target_text.setPlainText(source_text)
    
    @Slot()
    def translate_text(self):
        """Start the translation process."""
        # Get the input data
        source_text = self.source_text.toPlainText()
        if not source_text:
            self.statusBar.showMessage("Please enter text to translate", 3000)
            return

        provider = self.provider_combo.currentText()
        
        # Get the model ID from the item data rather than the display text
        model_index = self.model_combo.currentIndex()
        if model_index >= 0:
            model = self.model_combo.itemData(model_index)
        else:
            # Fallback to text if no item data (for custom models)
            model = self.model_combo.currentText()
        
        source_lang = self.source_language_combo.currentText()
        target_lang = self.target_language_combo.currentText()

        # Save current settings
        self.save_current_settings()

        # Debug: Print settings information
        print(f"DEBUG: Checking API key for provider: {provider}")
        api_key = self.settings.get_api_key(provider)
        print(f"DEBUG: API key from settings: {'[SET]' if api_key else '[NOT SET]'}")

        # Check if API key is set in settings
        if not api_key:
            print("DEBUG: API key is missing, showing settings dialog")
            QMessageBox.warning(
                self,
                "API Key Missing",
                f"API key for {provider} is not set. Please set it in API Settings."
            )
            self.show_api_settings()

            # After showing settings dialog, check again
            api_key = self.settings.get_api_key(provider)
            print(f"DEBUG: After dialog, API key: {'[SET]' if api_key else '[NOT SET]'}")

            if not api_key:
                return

        # Check additional fields if needed
        provider_class = get_provider_class(provider)
        additional_fields = provider_class.get_additional_fields()
        missing_fields = []

        for field_name in additional_fields.keys():
            field_value = self.settings.get_api_field(provider, field_name)
            print(f"DEBUG: Additional field {field_name}: {'[SET]' if field_value else '[NOT SET]'}")
            if not field_value:
                missing_fields.append(field_name)

        if missing_fields:
            print(f"DEBUG: Missing fields: {missing_fields}")
            QMessageBox.warning(
                self,
                "Missing Configuration",
                f"Additional configuration for {provider} is missing: {', '.join(missing_fields)}. Please set it in API Settings."
            )
            self.show_api_settings()
            return

        # Debug: Check if provider class can see the API key
        try:
            provider_instance = provider_class()
            provider_instance.set_api_key(api_key)
            for field_name in additional_fields.keys():
                field_value = self.settings.get_api_field(provider, field_name)
                if hasattr(provider_instance, f"set_{field_name}"):
                    getattr(provider_instance, f"set_{field_name}")(field_value)

            print(f"DEBUG: Provider instance created with API key")
        except Exception as e:
            print(f"DEBUG: Error creating provider instance: {str(e)}")

        # Update UI during translation
        self.translate_button.setEnabled(False)
        self.statusBar.showMessage(f"Translating with {provider} {model}...")
        self.target_text.setPlainText("Translating...")

        # Start worker thread
        self.translation_worker = TranslationWorker(
            provider, model, source_text, source_lang, target_lang
        )
        self.translation_worker.finished.connect(self.on_translation_finished)
        self.translation_worker.start()
        
    @Slot(str, bool)
    def on_translation_finished(self, result, success):
        """Handle the translation process completion."""
        self.translate_button.setEnabled(True)
        
        if success:
            self.target_text.setPlainText(result)
            self.statusBar.showMessage("Translation completed", 3000)
        else:
            self.target_text.setPlainText("")
            self.statusBar.showMessage(f"Translation error: {result}", 5000)
            QMessageBox.critical(self, "Translation Error", result)
    
    @Slot()
    def copy_translation(self):
        """Copy the translation to the clipboard."""
        translation = self.target_text.toPlainText()
        if translation:
            clipboard = QApplication.clipboard()
            clipboard.setText(translation)
            self.statusBar.showMessage("Translation copied to clipboard", 2000)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save settings before closing
        self.save_current_settings()
        event.accept()