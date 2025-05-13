from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QDialogButtonBox, 
    QRadioButton, QButtonGroup, QGroupBox, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QPalette


class ThemePreviewFrame(QFrame):
    """Widget to preview a theme."""
    
    def __init__(self, theme_name, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.setup_ui()
        self.apply_theme()
    
    def setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel(f"{self.theme_name.title()} Theme")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Sample text
        self.sample_text = QLabel("This is how text would appear in this theme.")
        self.sample_text.setWordWrap(True)
        self.sample_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.sample_text)
        
        # Sample button
        self.sample_button = QPushButton("Sample Button")
        layout.addWidget(self.sample_button)
        
        # Set fixed size
        self.setFixedSize(200, 150)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
    
    def apply_theme(self):
        """Apply the theme preview styles."""
        if self.theme_name == "light":
            self.setStyleSheet("""
                ThemePreviewFrame {
                    background-color: #f0f0f0;
                    color: #000000;
                }
                QLabel {
                    color: #000000;
                }
                QPushButton {
                    background-color: #e0e0e0;
                    color: #000000;
                    border: 1px solid #a0a0a0;
                    border-radius: 4px;
                    padding: 4px;
                }
            """)
        elif self.theme_name == "dark":
            self.setStyleSheet("""
                ThemePreviewFrame {
                    background-color: #2d2d2d;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    color: #ffffff;
                    border: 1px solid #505050;
                    border-radius: 4px;
                    padding: 4px;
                }
            """)
        elif self.theme_name == "special_dark":
            self.setStyleSheet("""
                ThemePreviewFrame {
                    background-color: #000000;
                    color: #ffffff;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #1a1a1a;
                    color: #FF0066;
                    border: 1px solid #FF0066;
                    border-radius: 4px;
                    padding: 4px;
                }
            """)


class ThemeSettingsDialog(QDialog):
    """Dialog for managing application themes."""
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        
        self.setup_ui()
        self.load_current_theme()
    
    def setup_ui(self):
        """Set up the UI components."""
        self.setWindowTitle("Theme Settings")
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout(self)
        
        # Theme selection group
        self.theme_group = QGroupBox("Select Theme")
        theme_layout = QVBoxLayout(self.theme_group)
        
        # Theme radio buttons
        self.theme_buttons = QButtonGroup(self)
        
        # Light theme
        self.light_theme_button = QRadioButton("Light Theme")
        self.theme_buttons.addButton(self.light_theme_button, 0)
        theme_layout.addWidget(self.light_theme_button)
        
        # Dark theme
        self.dark_theme_button = QRadioButton("Dark Theme")
        self.theme_buttons.addButton(self.dark_theme_button, 1)
        theme_layout.addWidget(self.dark_theme_button)
        
        # Special dark theme
        self.special_dark_theme_button = QRadioButton("Special Dark (Black with Raspberry Pink)")
        self.theme_buttons.addButton(self.special_dark_theme_button, 2)
        theme_layout.addWidget(self.special_dark_theme_button)
        
        layout.addWidget(self.theme_group)
        
        # Theme preview area
        preview_label = QLabel("Theme Preview:")
        layout.addWidget(preview_label)
        
        preview_layout = QHBoxLayout()
        
        # Light theme preview
        self.light_preview = ThemePreviewFrame("light")
        preview_layout.addWidget(self.light_preview)
        
        # Dark theme preview
        self.dark_preview = ThemePreviewFrame("dark")
        preview_layout.addWidget(self.dark_preview)
        
        # Special dark theme preview
        self.special_dark_preview = ThemePreviewFrame("special_dark")
        preview_layout.addWidget(self.special_dark_preview)
        
        layout.addLayout(preview_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def load_current_theme(self):
        """Load the current theme setting."""
        current_theme = self.settings.get_theme()
        
        if current_theme == "light":
            self.light_theme_button.setChecked(True)
        elif current_theme == "dark":
            self.dark_theme_button.setChecked(True)
        elif current_theme == "special_dark":
            self.special_dark_theme_button.setChecked(True)
        else:
            # Default to light theme
            self.light_theme_button.setChecked(True)
    
    def get_selected_theme(self):
        """Get the selected theme."""
        if self.light_theme_button.isChecked():
            return "light"
        elif self.dark_theme_button.isChecked():
            return "dark"
        elif self.special_dark_theme_button.isChecked():
            return "special_dark"
        else:
            return "light"  # Default
    
    def accept(self):
        """Save the selected theme when the dialog is accepted."""
        selected_theme = self.get_selected_theme()
        self.settings.set_theme(selected_theme)
        self.settings.save()
        super().accept()
