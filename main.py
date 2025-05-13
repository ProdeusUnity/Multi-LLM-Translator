#!/usr/bin/env python3
import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QFile, QTextStream, QResource
from PySide6.QtGui import QPalette, QColor
from ui.main_window import MainWindow
from config.settings import AppSettings
from utils.encryption import initialize_encryption


def setup_theme(app, settings):
    """Set up the application theme based on user preferences."""
    theme = settings.get_theme()
    
    # Reset to default palette first to avoid theme mixing issues
    app.setPalette(QApplication.style().standardPalette())
    app.setStyleSheet("")
    
    theme_functions = {
        "light": apply_light_theme,
        "dark": apply_dark_theme,
        "special_dark": apply_special_dark_theme
    }
    
    # Apply the selected theme or fallback to light if theme not found
    theme_func = theme_functions.get(theme, apply_light_theme)
    theme_func(app)


def apply_light_theme(app):
    """Apply the light theme with pure white background and black text."""
    palette = QPalette()
    
    # Text colors - Black
    palette.setColor(QPalette.WindowText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(0, 0, 0))
    palette.setColor(QPalette.ButtonText, QColor(0, 0, 0))
    palette.setColor(QPalette.BrightText, QColor(0, 0, 0))
    
    # Background colors - Pure White
    palette.setColor(QPalette.Window, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(245, 245, 245))
    
    # Button colors
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    
    # Selection colors
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Tooltip colors
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    
    # Link color
    palette.setColor(QPalette.Link, QColor(0, 0, 255))
    palette.setColor(QPalette.LinkVisited, QColor(128, 0, 128))
    
    # Apply the palette
    app.setPalette(palette)
    
    # Simple light theme stylesheet
    light_style = """
    QWidget {
        background-color: #FFFFFF;
        color: #000000;
    }
    
    QPushButton {
        background-color: #F0F0F0;
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 5px;
    }
    
    QPushButton:hover {
        background-color: #E0E0E0;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #FFFFFF;
        border: 1px solid #CCCCCC;
        border-radius: 4px;
        padding: 2px;
    }
    """
    
    app.setStyleSheet(light_style)


def apply_dark_theme(app):
    """Apply a dark theme with midnight black background and white text."""
    palette = QPalette()
    
    # Text colors - Pure White
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
    
    # Background colors - Midnight Black
    palette.setColor(QPalette.Window, QColor(0, 0, 0))
    palette.setColor(QPalette.Base, QColor(0, 0, 0))
    palette.setColor(QPalette.AlternateBase, QColor(15, 15, 15))
    
    # Button colors
    palette.setColor(QPalette.Button, QColor(0, 0, 0))
    
    # Selection colors
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    
    # Tooltip colors
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    
    # Link color
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.LinkVisited, QColor(150, 80, 220))
    
    # Disabled colors
    palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 128, 128))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 128, 128))
    
    # Apply the palette
    app.setPalette(palette)
    
    # Dark theme stylesheet
    dark_style = """
    QWidget {
        background-color: #000000;
        color: #FFFFFF;
    }
    
    QToolBar, QStatusBar {
        background-color: #000000;
        border: none;
    }
    
    QPushButton {
        background-color: #000000;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 5px;
        color: #FFFFFF;
    }
    
    QPushButton:hover {
        background-color: #2A2A2A;
    }
    
    QPushButton:pressed {
        background-color: #3A3A3A;
    }
    
    QLineEdit, QTextEdit, QPlainTextEdit {
        background-color: #000000;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 2px;
        color: #FFFFFF;
    }
    
    QComboBox {
        background-color: #000000;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 2px;
        color: #FFFFFF;
    }
    
    QTabBar::tab {
        background-color: #000000;
        border: 1px solid #555555;
        padding: 5px;
        color: #FFFFFF;
    }
    
    QTabBar::tab:selected {
        background-color: #2A2A2A;
    }
    
    QMenuBar, QMenu {
        background-color: #000000;
        color: #FFFFFF;
    }
    """
    
    app.setStyleSheet(dark_style)


def apply_special_dark_theme(app):
    """Apply special dark theme with raspberry pink highlights."""
    try:
        palette = QPalette()
        
        # Primary color - Raspberry pink (keeping the original color)
        primary_color = QColor("#FF0066")
        
        # Text colors - Using the original pink color for text
        palette.setColor(QPalette.WindowText, QColor("#FF0066"))
        palette.setColor(QPalette.Text, QColor("#FF0066"))
        palette.setColor(QPalette.ButtonText, QColor("#FF0066"))
        palette.setColor(QPalette.BrightText, QColor("#FF0066"))
        
        # Background colors - Midnight black
        palette.setColor(QPalette.Window, QColor(0, 0, 0))
        palette.setColor(QPalette.Base, QColor(0, 0, 0))
        palette.setColor(QPalette.AlternateBase, QColor(15, 15, 15))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(0, 0, 0))
        
        # Selection colors
        palette.setColor(QPalette.Highlight, primary_color)
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        
        # Tooltip colors
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor("#FF0066"))
        
        # Link color
        palette.setColor(QPalette.Link, primary_color)
        palette.setColor(QPalette.LinkVisited, QColor(220, 80, 150))
        
        # Disabled colors
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(128, 0, 32))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(128, 0, 32))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(128, 0, 32))
        
        # Apply the palette
        app.setPalette(palette)
        
        # Base style for special dark theme - keeping original pink color
        base_style = """
        QWidget {
            background-color: #000000;
            color: #FF0066;
        }
        
        QToolBar, QStatusBar {
            background-color: #000000;
            border: none;
        }
        
        QPushButton {
            background-color: #000000;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 5px;
            color: #FF0066;
        }
        
        QPushButton:hover {
            background-color: #000000;
            color: #FF0066;
        }
        
        QPushButton:pressed {
            background-color: #CC0052;
        }
        
        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #000000;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 2px;
            color: #FF0066;
        }
        
        QComboBox {
            background-color: #000000;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 2px;
            color: #FF0066;
        }
        
        QComboBox::drop-down {
            background-color: #000000;
            color: #FF0066;
        }
        
        QComboBox QAbstractItemView {
            background-color: #000000;
            color: #FF0066;
            selection-background-color: #FF0066;
            selection-color: #000000;
        }
        
        QTabWidget::pane {
            border: 1px solid #555555;
        }
        
        QTabBar::tab {
            background-color: #000000;
            border: 1px solid #555555;
            padding: 5px;
            color: #FF0066;
        }
        
        QTabBar::tab:selected {
            background-color: #FF0066;
            color: #000000;
        }
        
        QMenuBar {
            background-color: #000000;
            color: #FF0066;
        }
        
        QMenuBar::item:selected {
            background-color: #FF0066;
            color: #000000;
        }
        
        QMenu {
            background-color: #000000;
            border: 1px solid #555555;
            color: #FF0066;
        }
        
        QMenu::item:selected {
            background-color: #000000;
            color: #FF0066;
        }
        
        QScrollBar:vertical {
            background-color: #000000;
            width: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background-color: #000000;
            border-radius: 6px;
        }
        
        QScrollBar::handle:vertical:hover {
            background-color: #FF0066;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            background-color: #000000;
            height: 12px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background-color: #000000;
            border-radius: 6px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background-color: #FF0066;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        
        QCheckBox, QRadioButton {
            color: #FF0066;
        }
        
        QCheckBox::indicator:checked, QRadioButton::indicator:checked {
            background-color: #FF0066;
            border: 1px solid #555555;
        }
        
        QSlider::handle {
            background-color: #FF0066;
            border-radius: 7px;
        }
        
        QSlider::groove {
            background-color: #555555;
        }
        
        QProgressBar {
            background-color: #000000;
            border: 1px solid #555555;
            border-radius: 4px;
            text-align: center;
            color: #FF0066;
        }
        
        QProgressBar::chunk {
            background-color: #FF0066;
            width: 1px;
        }
        
        QHeaderView::section {
            background-color: #000000;
            color: #FF0066;
            padding: 4px;
            border: 1px solid #555555;
        }
        
        QTableView {
            gridline-color: #555555;
            background-color: #000000;
            color: #FF0066;
            selection-background-color: #FF0066;
            selection-color: #000000;
        }
        """
        
        app.setStyleSheet(base_style)
    except Exception as e:
        print(f"Error applying special dark theme: {e}")
        # Fallback to standard dark theme
        apply_dark_theme(app)


def main():
    try:
        # Create application directory if it doesn't exist
        app_dir = os.path.join(os.path.expanduser("~"), ".translator_app")
        os.makedirs(app_dir, exist_ok=True)
        
        # Initialize encryption for API keys
        initialize_encryption()
        
        # Create the Qt application
        app = QApplication(sys.argv)
        app.setApplicationName("AI Translator")
        app.setOrganizationName("AITranslator")
        
        # Load application settings
        settings = AppSettings()
        
        # Set up the theme
        setup_theme(app, settings)
        
        # Create and show the main window
        window = MainWindow(settings)
        window.show()
        
        # Start the application event loop
        sys.exit(app.exec())
    except Exception as e:
        print(f"Critical error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()